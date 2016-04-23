
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import tempfile

import sublime

from ..anaconda_lib.anaconda_plugin import anaconda_helpers
from ..anaconda_lib.helpers import get_settings, file_directory
from ..anaconda_lib.anaconda_plugin import completion, Worker, is_code

ags = anaconda_helpers.get_settings


class RustCompletionEventListener(completion.AnacondaCompletionEventListener):
    """AnacondaRUST completion event listener class
    """

    _just_completed = False

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
            RustCompletionEventListener._just_completed = True

            return (cpl, completion_flags)

        code = view.substr(sublime.Region(0, view.size()))
        # the JonServer deletes the temp file so we don't worry
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
        Worker().execute(self._complete, **data)

    def on_modified(self, view):
        """Called after changes has been made to a view.
        """

        return
