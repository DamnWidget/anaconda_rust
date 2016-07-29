
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

try:
    from ._rustanaconda import lib, ffi
except ImportError:
    from ._rustanaconda_ctypes import lib, ctypes


def _c_cast(ptr):
    """Cast a C char pointer into a Python owned string
    """

    try:
        return ffi.string(ptr)
    except NameError:
        return ctypes.cast(ptr, ctypes.c_char_p).value


__all__ = ['lib']
