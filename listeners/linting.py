
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

from ..anaconda_lib.sublime import run_linter
from ..anaconda_lib.anaconda_plugin import linting


class BackgroundLinter(linting.BackgroundLinter):
    """Background linter, can be turned off via plugin settings
    """

    def __init__(self):
        kwargs = {'lang': 'rust', 'linter': run_linter}
        super(BackgroundLinter, self).__init__(**kwargs)
        self.check_auto_lint = True

    def on_modified(self, view):
        pass
