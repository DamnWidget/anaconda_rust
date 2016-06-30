
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import tempfile
from functools import partial

import sublime

from ..anaconda_lib import RACER_VERSION
from ..anaconda_lib.anaconda_plugin import is_code, doc
from ..anaconda_lib.anaconda_plugin import Worker, Callback
from ..anaconda_lib.helpers import get_settings, file_directory


class RustDoc(doc.AnacondaDoc):
    """Get documenatation for the object under the cursor
    """

    def run(self, edit):
        if self.documentation is not None:
            return self.print_doc(edit)

        try:
            code = self.view.substr(sublime.Region(0, self.view.size()))
            # the JsonServer should delete the tmp file but we add a timeout
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
                'method': 'doc',
                'handler': 'racer'
            }

            Worker().execute(
                Callback(
                    on_success=self.prepare_data,
                    on_failure=partial(self.clean_tmp_file, path),
                    on_timeout=partial(self.clean_tmp_file, path)
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

    def clean_tmp_file(self, path, data):
        """Clean the tmp file at timeout
        """

        try:
            os.remove(path)
        except:
            pass
