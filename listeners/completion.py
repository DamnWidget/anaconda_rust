
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import sublime

from anaconda_rust.anaconda_lib.helpers import get_settings
from anaconda_rust.anaconda_lib.anaconda_plugin import Callback
from anaconda_rust.anaconda_lib.anaconda_plugin import anaconda_helpers
from anaconda_rust.anaconda_lib.anaconda_plugin import completion, Worker, is_code

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
        row, col = view.rowcol(locations[0])
        racer = get_settings(view, 'racer_binary_path', 'racer')
        if racer == '':
            racer = 'racer'

        data = {
            'vid': view.id(),
            'filename': view.file_name(),
            'settings': {
                'racer_binary_path': racer,
                'rust_src_path': get_settings(view, 'rust_src_path'),
                'row': row,
                'col': col,
                'source': code,
            },
            'method': 'autocomplete',
            'handler': 'racer'
        }
        Worker().execute(
            Callback(
                on_success=self._complete,
                on_failure=self._on_failure,
                on_timeout=self._on_timeout
            ),
            **data
        )

    def on_modified(self, view):
        """Called after changes has been made to a view.
        """

        return

    def _on_timeout(self, data):
        """Log into the ST3 console
        """

        print('Rust completion timed out')

    def _on_failure(self, data):
        """Log into the ST3 console
        """

        print('anaconda_racer: completion error')
        print(data['error'])
