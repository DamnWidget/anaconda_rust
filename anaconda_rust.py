
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

"""AnacondaRUST is a Rust IDE plugin for Sublime Text 3
"""

from .plugin_version import anaconda_required_version

from .anaconda_lib.anaconda_plugin import anaconda_version

if anaconda_required_version > anaconda_version:
    raise RuntimeError(
        'AnacondaRUST requires version {} or better of anaconda but {} '
        'is installed'.format(
            '.'.join([str(i) for i in anaconda_required_version]),
            '.'.join([str(i) for i in anaconda_version])
        )
    )

from .commands import *
from .listeners import *
