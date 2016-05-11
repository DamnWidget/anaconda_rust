
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import tempfile

try:
    import sublime
except ImportError:
    # we can't import sublime module outside ST3 context
    pass

from .anaconda_plugin import anaconda_helpers


def get_settings(view, name, default=None):
    """Get settings
    """

    if view is None:
        return None

    plugin_settings = sublime.load_settings('AnacondaRUST.sublime-settings')
    return view.settings().get(name, plugin_settings.get(name, default))


def set_setting(view, name, value):
    """Set settings
    """

    if view is None:
        return

    view.settings().set(name, value)


def file_directory():
    """Returns the given file directory
    """

    if int(sublime.version()) >= 3080:
        # extract_variables was added to ST3 rev 3080
        return sublime.active_window().extract_variables().get('file_path')

    folders = sublime.active_window().folders()
    if len(folders) > 0:
        return folders[0]

    return tempfile.gettempdir()


# reuse anaconda helper functions
get_view = anaconda_helpers.get_view
active_view = anaconda_helpers.active_view
check_linting = anaconda_helpers.check_linting
get_window_view = anaconda_helpers.get_window_view


__all__ = [
    'get_settings', 'active_view', 'get_view', 'get_window_view',
]
