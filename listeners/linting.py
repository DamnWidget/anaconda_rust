
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

from anaconda_rust.anaconda_lib.sublime import run_linter
from anaconda_rust.anaconda_lib.anaconda_plugin import linting
from anaconda_rust.anaconda_lib.helpers import check_linting, get_settings


class BackgroundLinter(linting.BackgroundLinter):
    """Background linter, can be turned off via plugin settings
    """

    def __init__(self):
        kwargs = {'lang': 'Rust', 'linter': run_linter}
        super(BackgroundLinter, self).__init__(**kwargs)
        self.check_auto_lint = True

    def on_modified(self, view):
        """Rustc can only work in files not in buffers
        """

        if check_linting(view, 0, code=self.lang.lower()):
            # remove prvious linting marks if configured to do so
            if not get_settings(view, 'anaconda_linter_persistent', False):
                linting.erase_lint_marks(view)
        else:
            self._erase_marks_if_no_linting(view)
