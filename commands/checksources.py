
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import sublime
import sublime_plugin

from anaconda_rust.anaconda_lib import check_rust_sources, RUST_VERSION


class CheckRustSources(sublime_plugin.WindowCommand):
    """Check rust sources and donwload them if needed
    """

    def run(self):
        sublime.set_timeout(check_rust_sources(RUST_VERSION), 0)
