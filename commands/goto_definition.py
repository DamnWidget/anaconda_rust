
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import tempfile
from functools import partial

import sublime
import sublime_plugin

from ..anaconda_lib.anaconda_plugin import is_code
from ..anaconda_lib.anaconda_plugin import JediUsages
from ..anaconda_lib.anaconda_plugin import Worker, Callback
from ..anaconda_lib.helpers import get_settings, file_directory


class RustGoto(sublime_plugin.TextCommand):
    """Excute racer find-definition command in a file
    """

    def run(self, edit):
        try:
            code = self.view.substr(sublime.Region(0, self.view.size()))
            # the JonServer deletes the temp file so we don't worry
            fd, path = tempfile.mkstemp(suffix=".rs", dir=file_directory())
            with os.fdopen(fd, "w") as tmp:
                tmp.write(code)

            row, col = self.view.rowcol(self.view.sel()[0].begin())
            racer = get_settings(self.view, 'racer_binary_path', 'racer')
            if racer == '':
                racer = 'racer'

            data = {
                'vid': self.view.id(),
                'filename': path,
                'settings': {
                    'racer_binary_path': racer,
                    'rust_src_path': get_settings(self.view, 'rust_src_path'),
                    'row': row,
                    'col': col
                },
                'method': 'goto',
                'handler': 'racer'
            }
            Worker().execute(
                Callback(
                    on_success=partial(JediUsages(self).process, False),
                    on_timeout=partial(self.clean_tmp_file, path)
                ),
                **data
            )
            Worker().execute(partial(JediUsages(self).process, False), **data)
        except:
            pass

    def is_enabled(self):
        """Determine if this command is enabled or not
        """

        if len(sublime.active_window().views()) == 0:
            return False

        return is_code(self.view, lang='rust')

    def clean_tmp_file(self, path):
        """Clean the tmp file at timeout
        """

        try:
            os.remove(path)
        except:
            pass
