
# Copyright (C) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import sys
import shlex
import logging
import subprocess
from os.path import join, dirname
from multiprocessing import cpu_count
from contextlib import contextmanager
from subprocess import PIPE, check_output, Popen

from cffi_compiler import Offline, OfflineCompilerError


class CompilationError(RuntimeError):
    """Raised on compilation errors
    """


class Compile():
    """Compile rust-anaconda Cargo
    """

    def __init__(self, version, settings, force=False):
        self.__version = version
        self.__settings = settings
        self.__force = force
        self.__src_path = None
        self.__libpath = None

    @property
    def cargo(self):
        """Return back the cargo binary path
        """

        return self.__settings.get('cargo_path', 'cargo')

    @property
    def srcpath(self):
        """Return back the rust-anaconda source path
        """

        if self.__src_path is None:
            file_name = os.path.abspath(__file__)
            self.__src_path = join(dirname(dirname(dirname(
                    dirname(file_name)))), 'rust-anaconda')
        return self.__src_path

    @property
    def libpath(self):
        """Return back the rust-anaconda library path
        """

        if self.__libpath is None:
            self.__libpath = join(dirname(dirname(__file__)), 'rust_anaconda')
        return self.__libpath

    @property
    def lib_ext(self):
        """Return back the library extension in the running platform
        """

        return {'darwin': 'dylib', 'linux': 'so', 'linux2': 'so'}.get(
            sys.platform, 'dll'
        )

    @property
    def libname(self):
        """Return back the shared library name
        """

        return 'librustanaconda-{0}.{1}'.format(self.__version, self.lib_ext)

    @property
    def binname(self):
        """Return back the binary name
        """

        return {'win32': 'rustfmt.exe'}.get(sys.platform, 'rustfmt')

    @property
    def liborigname(self):
        """Return back the shared library name as compiled by cargo
        """

        return 'librustanaconda.{0}'.format(self.lib_ext)

    @property
    def env(self):
        """Return back a dict with ready to use environment variables
        """

        _env = os.environ.copy()
        env = {}
        for key in _env:
            env[str(key)] = str(_env[key])

        env['RUST_SRC_PATH'] = self.__settings.get(
            'rust_src_path', _env.get('RUST_SRC_PATH', '')
        )

    @property
    def already_compiled(self):
        """
        Return True if thr target has been
        already compiled, otherwise returns False
        """

        return os.path.exists(join(self.libpath, self.libname))

    @contextmanager
    def compilation_dir(self):
        """Context manager to compile rust-anaconda in the right directory
        """

        currdir = os.getcwd()
        os.chdir(self.srcpath)
        lib = join(self.srcpath, 'target', 'release', self.liborigname)
        cbin = join(self.srcpath, 'target', 'release', self.binname)
        if self.__force:
            check_output(shlex.split('{0} clean'.format(self.cargo)))

        err = None
        try:
            yield
        except Exception as e:
            err = e
        finally:
            os.chdir(currdir)
            if err is not None:
                raise(err)

        if os.path.exists(lib):
            nlib = join(self.libpath, self.libname)
            try:
                os.rename(lib, nlib)
            except Exception as error:
                logging.error(error)
                raise CompilationError(
                    'while renaming {0} to {1}: {2}'.format(lib, nlib, error))

        if os.path.exists(cbin):
            nbin = join(self.libpath, self.binname)
            try:
                os.rename(cbin, nbin)
            except Exception as error:
                logging.error(error)
                raise CompilationError(
                    'while renaming {0} to {1}: {2}'.format(cbin, nbin, error))

    def compile(self):
        """Compile the rust-anaconda cargo
        """

        if self.already_compiled and not self.__force:
            return 'Already compiled'

        result = ''
        with self.compilation_dir():
            args = shlex.split('{0} build --release -j {1}'.format(
                self.cargo, cpu_count()), posix=os.name != 'nt'
            )

            kwargs = {}

            if os.name == 'nt':
                sinfo = subprocess.STARTUPINFO()
                sinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                kwargs['startupinfo'] = sinfo

            kwargs['cwd'] = os.getcwd()
            cargo = Popen(
                args, stdout=PIPE, stderr=PIPE, env=self.env,
                **kwargs
            )
            out, err = cargo.communicate()
            result = out.decode() if sys.version_info >= (3, ) else out
            if err is not None and len(err) > 0:
                if cargo.returncode != 0:
                    if sys.version_info >= (3, ):
                        raise(CompilationError(err.decode()))
                    raise(CompilationError(err))
                result += err.decode() if sys.version_info >= (3,) else err

        # compilation was successful, let's compile ffi-off-line now
        self._compile_cffi()

        logging.info(result)
        return result

    def _compile_cffi(self):
        """Compile the cffi-off-line library if CFFI is available
        """

        try:
            from cffi import FFI as _ffi
            del _ffi
        except ImportError:
            logging.info(
                'CFFI is not installed falling back to ctypes (╯°□°）╯︵ ┻━┻')
            return

        with Offline(self.libname) as cffi_compiler:
            try:
                cffi_compiler.compile()
            except OfflineCompilerError as e:
                logging.error(e)


if __name__ == '__main__':
    app = sys.argv[0]
    if len(sys.argv) < 3:
        print(
            '{0} usage:\n\n{0} version cargo_path rust_src_path\n'.format(app)
        )
        sys.exit(1)

    version, cargo_path, rust_src_path = sys.argv[1], sys.argv[2], sys.argv[3]
    compiler = Compile(version, {
        'cargo_path': cargo_path, 'rust_src_path': rust_src_path
    })
    try:
        compiler.compile()
    except Exception as error:
        print('Error: {}'.format(error))
        sys.exit(1)
