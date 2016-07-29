
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

"""AnacondaRUST is a Rust IDE plugin for Sublime Text 3
"""

import os
import sublime

from anaconda_rust.plugin_version import anaconda_required_version

from anaconda_rust.anaconda_lib import check_rust_version
from anaconda_rust.anaconda_lib import prepare_anaconda_rust
from anaconda_rust.anaconda_lib import RUST_VERSION, ANACONDA_READY
from anaconda_rust.anaconda_lib.anaconda_plugin import anaconda_version

if anaconda_required_version > anaconda_version:
    raise RuntimeError(
        'AnacondaRUST requires version {} or better of anaconda but {} '
        'is installed'.format(
            '.'.join([str(i) for i in anaconda_required_version]),
            '.'.join([str(i) for i in anaconda_version])
        )
    )

from anaconda_rust.commands import *
from anaconda_rust.listeners import *


def plugin_loaded():
    """Called directly from sublime on plugin load
    """

    # determine the installed rust version
    rust_version = check_rust_version()
    if rust_version is None:
        sublime.error_message(
            'Anaconda can not determine which Rust version you have '
            'installed in your system, this can happen because one '
            'of the following:\n\n'
            '   * rustc is not in your PATH environment variable\n'
            '   * your environment variables are not inherited by ST3\n'
            '\n'
            'To solve the issue you can explicitly set the path to your '
            'rustc binary in the configuration.\n\nExecute \'Anaconda: '
            'Set Rustc Path\' command in your Control Palette'
        )
        return

    compile_path = os.path.join(
        os.path.dirname(__file__),
        'plugin', 'handlers_rust', 'rust_anaconda', 'compile.py'
    )

    ifile = os.path.join(os.path.dirname(__file__), '.installed_once')
    if not os.path.exists(ifile):
        cont = sublime.ok_cancel_dialog(
            'Seems like this is the first time that you run AnacondaRUST '
            'or that you never compiled the rust-anaconda environment in '
            'this installation.\n\nAnacondaRUST comes with a customized '
            'crate (rust-anaconda) that wraps \'rustfmt\' and \'racer\' '
            'into a shared library that is then used directly from the '
            'package Python code using FFI (CFFI or ctypes).\n\n'
            'AnacondaRUST needs to compile this crate in order to work, '
            'it compiles it using the \'cargo\' tool and the process could '
            'take between 3 and 10 mins depending on your processor cores '
            'and frequency. AnacondaRUST is gonna try to compile itself now.'
            'Do you want to proceed with the compilation or maybe you want '
            'to pospone it for later (AnacondaRUST will not work until '
            'you compile it)?.\n\nNote: you can always fire the compilaton '
            'process using the command palette \'Anaconda: Compile '
            'Rust-Anaconda Library\'', 'compile'
        )
        if cont:
            prepare_anaconda_rust(rust_version, compile_path, ifile)
