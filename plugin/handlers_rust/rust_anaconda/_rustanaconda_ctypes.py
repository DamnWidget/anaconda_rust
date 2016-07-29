
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import sys
import ctypes

lib = None


def load_library():
    """Load the librustanaconda library
    """

    ext = {'darwin': 'dylib', 'linux': 'so', 'linux2': 'so'}.get(
        sys.platform, 'dll'
    )
    try:
        lf = [
            f for f in os.listdir()
            if f.startswith('librustanaconda') and f.endswith(ext)
        ][0]
    except IndexError:
        raise RuntimeError('librustanaconda is not compiled!')

    l = ctypes.cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), lf))
    return l

if lib is None:
    lib = load_library()
