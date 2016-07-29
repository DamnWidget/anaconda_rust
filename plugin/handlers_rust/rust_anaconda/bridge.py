
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import ast
import sys

from .context import Context, lib


class GetVersion(Context):
    """Returns the rust-anaconda crate version as a Python string
    """

    def __enter__(self):
        """
        Call the get_version function from the underlying Rust library
        copy its value to a Python owned sring and free any Rust allocated mem
        """

        self._ptr = lib.get_version()
        if sys.version_info >= (3, ):
            return self.cast().decode()

        return self.cast()


class Format(Context):
    """Calls the underlying format from rust library
    """

    def __init__(self, code, config_path=None):
        if sys.version_info >= (3, 0):
            if type(code) is not bytes:
                code = bytes(code, 'utf8')
            if config_path is not None:
                if type(config_path) is not bytes:
                    config_path = bytes(config_path, 'utf8')
            else:
                config_path = b''
        else:
            if config_path is None:
                config_path = ''

        self.code = code
        self.config_path = config_path

        self.bin_path = os.path.join(
            os.path.dirname(__file__),
            {'win32': 'rustfmt.exe'}.get(sys.platform, 'rustfmt')
        )

    def __enter__(self):
        """
        Replace the standard output/error with a StringIO instance, call the
        rustfmt library command, store it's output in a variable and
        restore the standard output, this method doesn't allow mem in rust
        """

        try:
            self.format()
        except Exception as e:
            return 'error: {0}'.format(e)

    def format(self):
        """Call the underlying format rust function
        """

        self._ptr = lib.format(self.bin_path, self.code, self.config_path)
        r = self.cast().decode() if sys.version_info >= (3,) else self.cast()
        return r


class Complete(Context):
    """Returns a Python owned dictionary with a list of completions
    """

    def __init__(self, code, path, line, col):
        if sys.version_info >= (3,):
            if type(code) is not bytes:
                code = bytes(code, 'utf8')
            if type(path) is not bytes:
                path = bytes(path, 'utf8')

        self.code = code
        self.path = path
        self.line = line
        self.col = col
        super(Complete, self).__init__()

    def __enter__(self):
        """
        Call the completion rust function parse its output into a Python
        owned memory list of dicts and return it. This method allocates memory
        """

        try:
            return self.complete()
        except Exception as e:
            return 'error: {0}'.format(e)

    def complete(self):
        """Run the underlying complete function
        """

        self._ptr = lib.complete(self.code, self.path, self.line, self.col)
        r = self.cast().decode() if sys.version_info >= (3,) else self.cast()
        return [
            dict(match=l[0], snippet=l[1], path=l[2], mtype=l[3], ctx=l[4])
            for l in (
                line.split('\t') for line in
                r.splitlines() if line.count('\t') == 4
            )
        ]


class Definitions(Complete):
    """Returns a Python memory owned list of possible definition locations
    """

    def __enter__(self):
        """
        Call the find_definition rust function parse its output into a Python
        owned memory list of dicts and return it. This method allocates memory
        """

        try:
            return self.find_definition()
        except Exception as e:
            return 'error: {0}'.format(e)

    def find_definition(self):
        """Run the underlying find_definition function
        """

        self._ptr = lib.find_definition(
            self.code, self.path, self.line, self.col)
        r = self.cast().decode() if sys.version_info >= (3,) else self.cast()
        return [
            dict(path=l[0], line=l[1], col=l[2])
            for l in (
                line.split('\t') for line in
                r.splitlines() if line.count('\t') == 2
            )
        ]


class Documentation(Complete):
    """Return a Python owned memory string
    """

    def __enter__(self):
        """Call the documentation rust function and return a Python owned str
        """

        try:
            return self.documentation()
        except Exception as e:
            return 'error: {0}'.format(e)

    def documentation(self):
        """Run the underlying documentation function
        """

        self._ptr = lib.documentation(
            self.code, self.path, self.line, self.col)
        r = self.cast().decode() if sys.version_info >= (3,) else self.cast()
        return ast.literal_eval(r)
