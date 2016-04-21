
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

from functools import partial

import sublime as st3_sublime

from .helpers import get_settings, active_view
from .anaconda_plugin import anaconda_sublime, Worker, Callback


def run_linter(view=None):
    """Run the linter for the given view
    """

    if view is None:
        view = active_view()

    if not get_settings(view, 'anaconda_rust_linting', False):
        return

    if view.file_name() in anaconda_sublime.ANACONDA['DISABLED']:
        anaconda_sublime.erase_lint_marks(view)
        return

    settings = {
        'rustc_binary_path': get_settings(view, 'rustc_binary_path', 'rustc')
    }

    text = view.substr(st3_sublime.Region(0, view.size()))
    data = {
        'vid': view.id(),
        'code': text,
        'settings': settings,
        'filename': view.file_name(),
        'method': 'lint',
        'handler': 'rust_linter'
    }

    callback = partial(anaconda_sublime.parse_results, **dict(code='rust'))
    Worker().execute(Callback(on_success=callback), **data)
