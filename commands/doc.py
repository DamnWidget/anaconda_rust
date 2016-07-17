
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import sublime

from anaconda_rust.anaconda_lib import RACER_VERSION
from anaconda_rust.anaconda_lib.helpers import get_settings
from anaconda_rust.anaconda_lib.anaconda_plugin import is_code, doc
from anaconda_rust.anaconda_lib.anaconda_plugin import Worker, Callback


class RustDoc(doc.AnacondaDoc):
    """Get documenatation for the object under the cursor
    """

    def run(self, edit):
        if self.documentation is not None:
            return self.print_doc(edit)

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
                'method': 'doc',
                'handler': 'racer'
            }

            Worker().execute(
                Callback(
                    on_success=self.prepare_data,
                    on_failure=self._on_failure,
                    on_timeout=self._on_timeout
                ),
                **data
            )
        except Exception as error:
            print(error)

    def is_enabled(self):
        """Determine if this command is enabled or not
        """

        if len(sublime.active_window().views()) == 0:
            return False

        if RACER_VERSION is not None and RACER_VERSION < (1, 2, 10):
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
