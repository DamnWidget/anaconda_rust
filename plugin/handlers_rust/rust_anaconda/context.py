
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

from .rustanaconda import lib, _c_cast


class Context(object):
    """All commands that allocate memory must inherit from this class
    """

    def __init__(self):
        self._ptr = None

    def __exit__(self):
        """Free any Rust allocated memory
        """

        lib.free_c_char_mem(self._ptr)

    def cast(self):
        """Cast a C pointer to char into a Python string
        """

        return _c_cast(self._ptr)
