
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import logging
import traceback

import sublime
import sublime_plugin

from anaconda_rust.anaconda_lib.anaconda_plugin import is_code
from anaconda_rust.anaconda_lib.anaconda_plugin import ProgressBar
from anaconda_rust.anaconda_lib import RUST_VERSION, ANACONDA_READY
from anaconda_rust.anaconda_lib.anaconda_plugin import Worker, Callback
from anaconda_rust.anaconda_lib.helpers import get_settings, get_window_view


class AnacondaRustFmt(sublime_plugin.TextCommand):
    """Execute rustfmt command in a file
    """

    data = None

    def run(self, edit):

        if self.data is not None:
            self.update_buffer(edit)
            return

        try:
            messages = {
                'start': 'Auto formatting file...',
                'end': 'done!',
                'fail': 'The auto formatting failed!',
                'timeout': 'The auto formatiing timed out!'
            }
            self.pbar = ProgressBar(messages)
            self.pbar.start()
            self.view.set_read_only(True)

            self.code = self.view.substr(
                sublime.Region(0, self.view.size())
            )

            config_path = get_settings(self.view, 'rust_rustfmt_config_path')
            if config_path is None or config_path == '':
                config_path = self._get_working_directory()

            data = {
                'vid': self.view.id(),
                'settings': {
                    'source': self.code,
                    'config_path': config_path
                },
                'method': 'format',
                'handler': 'rustfmt'
            }
            timeout = get_settings(self.view, 'rust_rustfmt_timeout', 1)

            callback = Callback(timeout=timeout)
            callback.on(success=self.prepare_data)
            callback.on(error=self.on_failure)
            callback.on(timeout=self.on_failure)

            Worker().execute(callback, **data)
        except:
            logging.error(traceback.format_exc())

    def is_enabled(self):
        """Determine if this command is enabled or not
        """

        if RUST_VERSION is None or not ANACONDA_READY:
            return False

        return is_code(self.view, lang='rust', ignore_comments=True)

    def on_failure(self, *args, **kwargs):
        """Called when callback return a failure or times out
        """

        self.pbar.terminate(status=self.pbar.Status.FAILURE)
        self.view.set_read_only(False)
        print(args[0]['error'])

    def prepare_data(self, data):
        """Prepare the returned data to overwrite our buffer
        """

        self.data = data
        self.pbar.terminate()
        self.view.set_read_only(False)
        self.view.run_command('anaconda_rust_fmt')

    def update_buffer(self, edit):
        """Update and reload the buffer
        """

        view = get_window_view(self.data['vid'])
        if self.code != self.data.get('output'):
            region = sublime.Region(0, view.size())
            view.replace(edit, region, self.data.get('output'))
            if get_settings(view, 'rust_format_on_save'):
                sublime.set_timeout(lambda: view.run_command('save'), 0)

        self.data = None
        self.code = None

    def _get_working_directory(self):
        """Return back the project file directory if any or current file one
        """

        pfilename = sublime.active_window().project_file_name()
        if pfilename is not None:
            return os.path.dirname(pfilename)

        return os.path.dirname(self.view.file_name())
