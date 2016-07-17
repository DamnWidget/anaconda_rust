
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import sublime_plugin

from anaconda_rust.anaconda_lib.helpers import get_settings
from anaconda_rust.anaconda_lib.anaconda_plugin import is_code


class AutoRustFmtListener(sublime_plugin.EventListener):
    """Anaconda auto RustFM event listener class
    """

    def on_pre_save(self, view):
        """Called just before the file is goign to be saved
        """

        if is_code(view, lang='rust', ignore_comments=True):
            if get_settings(view, 'rust_format_on_save', False):
                    view.run_command('anaconda_rust_fmt')
