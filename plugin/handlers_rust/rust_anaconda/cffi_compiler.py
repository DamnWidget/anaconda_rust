
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os


class OfflineCompilerError(RuntimeError):
    """Raised when error are encountered
    """


class Offline(object):
    """Compile a CFFI library off-line to speed things up
    """

    def __init__(self, libname):
        self.__path = os.path.dirname(__file__)
        self.__current_path = os.getcwd()
        self.libname = libname
        self.error = None

    def __enter__(self):
        """Cd into the compilation directory and return a ref to self
        """

        os.chdir(self.__path)
        return self

    def __exit__(self, *ext):
        """Delete intermediate files and go back to the previous directory
        """

        if self.error is None:
            os.unlink('_rustanaconda.c')
            os.unlink('_rustanaconda.o')

        os.chdir(self.__current_path)

    def compile(self):
        """Compile a Python ready to import C shared library for rust-anaconda
        """

        from cffi import FFI
        try:
            ffi = FFI()
            ffi.set_source('_rustanaconda', '', extra_objects=[self.libname])
            ffi.cdef('''// rustanaconda C definitions
void free_c_char_mem(char *);
char * format(char *, char *, char *);
char * get_version();
char * get_env(char *);
char * complete(char *, char *, uint32_t, uint32_t);
char * definitions(char *, char *, uint32_t, uint32_t);
char * documentation(char *, char *, uint32_t, uint32_t);''')
            ffi.compile(verbose=False)
        except Exception as e:
            self.error = 'while compiling ffi-off-line: {0}'.format(e)
            raise OfflineCompilerError(self.error)
