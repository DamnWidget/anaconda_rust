
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import logging
import traceback

import sublime
import sublime_plugin

from anaconda_rust.anaconda_lib.helpers import active_view
from anaconda_rust.anaconda_lib.anaconda_plugin import is_code


class AnacondaRustSetRustc(sublime_plugin.WindowCommand):
    """Set the rustc path
    """

    def run(self):
        self._settings = sublime.load_settings('AnacondaRUST.sublime-settings')  # noqa
        try:
            sublime.active_window().show_input_panel(
                "rustc path:", self.get_current_rustc_path(),
                self.update_rustc_settings, None, None
            )
        except:
            logging.error(traceback.format_exc())

    def update_rustc_settings(self, rustc_path):
        """Updates the project/user_settings  and adds/modifies the rustc path
        """

        if not os.path.exists(rustc_path):
            sublime.error_message('{} does not exists!'.format(rustc_path))
            return

        project_data = self.get_project_data()
        if project_data is not None:
            # Check if have settings set in the project settings
            if project_data.get('settings', False):

                try:
                    # Try to get the rustc key
                    project_data['settings'].get('rustc_binary_path', False)
                except AttributeError:
                    # If this happens your settings is a sting not a dict
                    sublime.message_dialog(
                        'Ops your project settings is messed up'
                    )
                else:
                    # Set the path and save the project
                    project_data['settings']['rustc_binary_path'] = rustc_path
                    self.save_project_data(project_data)
            else:
                # if settings key is not in project settings
                project_data.update({
                    'settings': {'rustc_binary_path': rustc_path}
                })
                self.save_project_data(project_data)
                AnacondaSetPythonBuilder().update_interpreter_build_system(
                    venv_path
                )
            return

        # there is no project, let's update the global settings :|
        self._settings.set('rustc_binary_path', rustc_path)

    def save_project_data(self, data):
        """Saves the provided data to the project settings
        """

        sublime.active_window().set_project_data(data)
        sublime.status_message("rustc path has been set successfuly")

    def get_project_data(self):
        """Return the project data for the current window
        """

        return sublime.active_window().project_data()

    def get_current_rustc_path(self):
        """Returns the current path from the settings if possible
        """

        try:
            return self.get_project_data()['settings']['rustc_binary_path']
        except:
            return self._settings.get('rustc_binary_path', '')

    def is_enabled(self):
        """Check is the command is enabled
        """

        return is_code(active_view(), lang='rust')
