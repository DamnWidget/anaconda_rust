
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

from functools import partial

import sublime
import sublime_plugin

from anaconda_rust.anaconda_lib.helpers import get_settings
from anaconda_rust.anaconda_lib.anaconda_plugin import is_code
from anaconda_rust.anaconda_lib.anaconda_plugin import JediUsages
from anaconda_rust.anaconda_lib.anaconda_plugin import Worker, Callback


class RustGoto(sublime_plugin.TextCommand):
    """Excute racer find-definition command in a file
    """

    def run(self, edit):
        try:
            code = self.view.substr(sublime.Region(0, self.view.size()))
            row, col = self.view.rowcol(self.view.sel()[0].begin())
            racer = get_settings(self.view, 'racer_binary_path', 'racer')
            if racer == '':
                racer = 'racer'

            data = {
                'vid': self.view.id(),
                'filename': self.view.file_name(),
                'settings': {
                    'racer_binary_path': racer,
                    'rust_src_path': get_settings(self.view, 'rust_src_path'),
                    'row': row,
                    'col': col,
                    'source': code
                },
                'method': 'goto',
                'handler': 'racer'
            }
            Worker().execute(
                Callback(
                    on_success=partial(JediUsages(self).process, False),
                    on_failure=self._on_failure,
                    on_timeout=self._on_timeout
                ),
                **data
            )
        except:
            pass

    def is_enabled(self):
        """Determine if this command is enabled or not
        """

        if len(sublime.active_window().views()) == 0:
            return False

        return is_code(self.view, lang='rust')

    def _on_failure(self, data):
        """Fired on failures from the callback
        """

        print('anaconda_racer: completion error')
        print(data['error'])

    def _on_timeout(self, data):
        """Fired when the callback times out
        """

        print('Rust goto definition timed out')
