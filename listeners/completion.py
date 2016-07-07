
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import tempfile
from functools import partial

import sublime

from ..anaconda_lib.anaconda_plugin import Callback
from ..anaconda_lib.anaconda_plugin import anaconda_helpers
from ..anaconda_lib.helpers import get_settings, file_directory
from ..anaconda_lib.anaconda_plugin import completion, Worker, is_code

ags = anaconda_helpers.get_settings


class RustCompletionEventListener(completion.AnacondaCompletionEventListener):
    """AnacondaRUST completion event listener class
    """

    def on_query_completions(self, view, prefix, locations):
        """Sublime Text autocompletion event handler
        """

        if not is_code(view, lang='rust'):
            return

        if self.ready_from_defer is True:
            completion_flags = 0

            if ags(view, 'suppress_word_completions', False):
                completion_flags = sublime.INHIBIT_WORD_COMPLETIONS

            if ags(view, 'suppress_explicit_completions', False):
                completion_flags = sublime.INHIBIT_EXPLICIT_COMPLETIONS

            cpl = self.completions
            self.completions = []
            self.ready_from_defer = False

            return (cpl, completion_flags)

        code = view.substr(sublime.Region(0, view.size()))
        # the JsonServer should delete the tmp file but we add a timeout
        fd, path = tempfile.mkstemp(suffix=".rs", dir=file_directory())
        with os.fdopen(fd, "w") as tmp:
            tmp.write(code)

        row, col = view.rowcol(locations[0])
        racer = get_settings(view, 'racer_binary_path', 'racer')
        if racer == '':
            racer = 'racer'

        data = {
            'vid': view.id(),
            'filename': path,
            'settings': {
                'racer_binary_path': racer,
                'rust_src_path': get_settings(view, 'rust_src_path'),
                'row': row,
                'col': col
            },
            'method': 'autocomplete',
            'handler': 'racer'
        }
        Worker().execute(
            Callback(
                on_success=self._complete,
                on_failure=partial(self.clean_tmp_file, path),
                on_timeout=partial(self.clean_tmp_file, path)
            ),
            **data
        )

    def on_modified(self, view):
        """Called after changes has been made to a view.
        """

        return

    def clean_tmp_file(self, path, data):
        """Clean the tmp file at  timeout and errors
        """

        print(data['error'])
        try:
            os.remove(path)
        except:
            pass
