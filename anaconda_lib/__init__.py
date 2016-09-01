
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import shlex
import tarfile
import tempfile
import traceback
import subprocess
import urllib.request

import sublime

from anaconda_rust.anaconda_lib.async_proc import AsyncProc
from anaconda_rust.anaconda_lib.anaconda_plugin import Callback
from anaconda_rust.anaconda_lib.anaconda_plugin import ProgressBar
from anaconda_rust.anaconda_lib.helpers import get_settings, active_view
from anaconda_rust.anaconda_lib.anaconda_plugin import anaconda_get_settings

RUST_VERSION = None
ANACONDA_READY = False


def check_rust_version():
    """Check the installed rust version
    """

    global RUST_VERSION

    pbar = ProgressBar({
        'start': 'Checking Rust version, please wait',
        'end': 'Rust version {} checked'.format(RUST_VERSION),
        'fail': 'Rust version check failed, check console logs',
        'timeout': ''
    })
    pbar.start()

    view = active_view()
    rustc = get_settings(view, 'rustc_binary_path', 'rustc')
    if rustc == '':
        rustc = 'rustc'

    env = os.environ.copy()
    rust_src_path = get_settings(view, 'rust_src_path')
    if rust_src_path is None or rust_src_path == '':
        rust_src_path = os.environ.get('RUST_SRC_PATH', '')

    env['RUST_SRC_PATH'] = rust_src_path

    try:
        data = subprocess.check_output([rustc, '-V'], env=env)
        RUST_VERSION = data.split()[1].decode()
        pbar.terminate()
    except Exception as error:
        pbar.terminate(status=pbar.Status.FAILURE)
        print('Can\'t determine rust version: {}'.format(error))
    else:
        return RUST_VERSION


class PanelListener:
    """Just listen to AsyncProc and update the inner panel
    """

    def __init__(self, proc, panel):
        self.proc = proc
        self.panel = panel

    def notify(self, proc, msg, err=False):
        """Notification msg coming from the proccess
        """

        if err is not False:
            self.err = True

        if proc is None or proc != self.proc:
            return

        self.panel.run_command(
            'append', {
                'characters': msg.decode(),
                'force': True, 'scroll_to_end': True
            }
        )

    def complete(self, proc):
        """The process has finished
        """

        if proc is None or proc != self.proc:
            return

        done = 'Compilation '
        if proc.status != proc.Status.DONE:
            done = '{} Success...'.format(done)
        else:
            done = '{} done with errors:\n{}'.format(done, proc.error)

        self.panel.run_command(
            'append',
            {'characters': done, 'force': True, 'scroll_to_end': True}
        )


def prepare_anaconda_rust(version, path, ifile):
    """
    This is probably the most important function in the whole package.
    It is responsible of:
        * Start a JsonServer for the current project if is not started yet
        * Compile librustanaconda for first time after package installation
        * Recompile librustanaconda on package updates
        * Compile a cffi-off-line Python shared lib module if cffi is present
        * Download the in use Rust version sources (if needed)
        * Set the RUST_SRC_PATH variable for the anaconda environment
        * Unlock the package if anaconda is ready
    """

    prpbar = ProgressBar({
        'start': (
            'Preparing anaconda rust environment, this may take a while, '
            'please wait, seriusly, wait, we are compiling rust-anaconda...'
        ),
        'end': 'Anaconda rust environment ready',
        'fail': 'Failed to prepare rust environment, check console logs',
        'timeout': 'Rust environment preparation timed out, retry in 5s'
    })
    prpbar.start()

    view = active_view()
    _panel = view.window().create_output_panel('anaconda_rust_notifications')
    _panel.run_command('append',
                       {'characters': 'Compiling AnacondaRUST', 'force': True})

    def _success(resp):
        """Callback for successful operations
        """
        global ANACONDA_READY
        print(resp['msg'])

        ANACONDA_READY = True
        prpbar.terminate()
        print('AnacondaRUST is ready, using rust-{}'.format(RUST_VERSION))
        pbar = ProgressBar({
            'start': 'Checking rust {} sources, please wait'.format(
                RUST_VERSION
            ),
            'end': 'Sources checked!',
            'fail': 'Sources check failed, look at the console output',
            'timeout': 'Sources check timed out, retrying in 5s'
        })
        pbar.start()

        try:
            check_rust_sources(version)
            pbar.terminate()
        except Exception as e:
            pbar.terminate(status=pbar.Status.FAILURE)
            print('AnacondaRUST: while checking rust sources: {}'.format(e))
            print(traceback.format_exc())
            sublime.error_message(
                'AnacondaRUST failed to check rust sources for version in '
                'use ({}), you can try to execute the checker again in a '
                'manually fashion using the Command Palette command '
                '\'Anaconda: Check Rust Sources\', if the problem persist '
                'you can try to follow the instructions to donwload the '
                'sources for your in use Rust version visiting '
                'https://github.com/DamnWidget/anaconda_rust/wiki/'
                'Download-Rust-Sources-manually'.format(version)
            )
        else:
            with open(ifile, 'w') as f:
                f.write('')

    def _failure(resp):
        """Callback for unssuccesful operations
        """

        prpbar.terminate(status=prpbar.Status.FAILURE)
        print('AnacondaRUST: can not prepare rust environment.')
        print('AnacondaRUST: {}'.format(resp['msg']))

    def _timeout():
        """Callback for timed out operations
        """

        prpbar.terminate(status=prpbar.Status.TIMEOUT)
        print('AnacondaRUST: prepare_anaconda_rust timed out...', end='')
        print('probably waiting for JsonServer...')
        print('AnacondaRUST: trying out again in 5s')
        sublime.set_timeout(lambda: prepare_anaconda_rust(version, path), 5000)

    def _communicate(p, cb, view):
        """Call p.communicate
        """

        try:
            timeout = get_settings(view, 'rust_anaconda_compile_timeout', 600)
            out, err = p.communicate(timeout=timeout * 1000)
        except subprocess.TimeoutExpired:
            p.kill()
            cb({'status': 'timed_out'})
            return

        if p.returncode != 0:
            cb({'status': 'failed', 'msg': err})
        else:
            cb({'status': 'succeeded', 'msg': out})

    rustc = get_settings(view, 'rustc_binary_path', 'rustc')
    src_path = get_settings(view, 'rust_src_path')
    env_src_path = os.environ.get('RUST_SRC_PATH', '')
    cargo = 'cargo'
    if len(rustc) > 0:
        cargo = os.path.join(os.path.dirname(rustc), 'cargo')

    timeout = get_settings(view, 'rust_anaconda_compile_timeout', 600)
    cb = Callback(
        timeout=timeout,
        on_success=_success,
        on_failure=_failure,
        on_timeout=_timeout
    )

    python = anaconda_get_settings(view, 'python_interpreter', 'python')
    args = shlex.split('{} {} {} {} {}'.format(
        python, path, version, cargo,
        src_path if len(src_path) > 0 else env_src_path
    ), posix=os.name != 'nt')
    p = AsyncProc(cb, args)

    listener = PanelListener(p, _panel)
    p.add_watcher(listener)
    sublime.set_timeout_async(lambda: p.run(), 0)


def check_rust_sources(version):
    """
    Check for the rust sources in the file
    system and download them if they are missing
    """

    src_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'rust_src')
    if not os.path.exists(src_path):
        # create src_path
        os.mkdir(src_path)

    rust_ver_src = os.path.join(src_path, RUST_VERSION)
    if not os.path.exists(rust_ver_src):
        dlname = ''
        tplname = 'rustc-{}-src.tar.gz'
        if 'nightly' in RUST_VERSION:
            dlname = tplname.format('nightly')
        elif 'beta' in RUST_VERSION:
            dlname = tplname.format('beta')
        else:
            dlname = tplname.format(RUST_VERSION)

        # donwload the rust sources for the in use rust version
        dlfile = os.path.join(tempfile.gettempdir(), dlname)
        with open(dlfile, 'wb') as f:
            dlurl = 'https://static.rust-lang.org/dist/{}'.format(dlname)
            print('AnacondaRUST: donwloading {}...'.format(dlname))
            with urllib.request.urlopen(dlurl) as resource:
                f.write(resource.read())

        # extract the tar file
        print('AnacondaRUST: extracting {}...'.format(dlfile))
        tmpdir = os.path.join(os.path.dirname(rust_ver_src), 'tmp')
        with tarfile.open(dlfile, 'r:gz') as tar:
            tar.extractall(tmpdir)

        # move the directory to it's final location
        os.rename(os.path.join(tmpdir, dlname.split('-src')[0]), rust_ver_src)

        # clean temp directory
        print('AnacondaRUST: cleaning up temp directory...')
        os.unlink(dlfile)
        os.rmdir(tmpdir)

        print('AnacondaRUST: rust sources for version {} installed'.format(
            RUST_VERSION)
        )
