
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import logging
import traceback

import sublime
import sublime_plugin

from ..anaconda_lib.anaconda_plugin import is_code
from ..anaconda_lib.anaconda_plugin import ProgressBar
from ..anaconda_lib.anaconda_plugin import Worker, Callback
from ..anaconda_lib.helpers import get_settings, get_window_view


class AnacondaRustFmt(sublime_plugin.TextCommand):
    """Execute rustfmt command in a file
    """

    output = None

    def run(self, edit):

        if self.output is None:
            try:
                messages = {
                    'start': 'Auto formatting file...',
                    'end': 'done!',
                    'fail': 'The auto formatting failed!',
                    'timeout': 'The auto formatiing timed out!'
                }
                self.pbar = ProgressBar(messages)
                self.pbar.start()
                self.view.set_read_only(True)

                data = {
                    'vid': self.view.id(),
                    'filename': self.view.file_name(),
                    'method': 'format',
                    'handler': 'rustfmt'
                }
                timeout = get_settings(self.view, 'rust_rustfmt_timeout', 1)

                callback = Callback(timeout=timeout)
                callback.on(success=self.prepare_data)
                callback.on(error=self.on_failure)
                callback.on(timeout=self.on_failure)

                Worker().execute(callback, **data)
            except:
                logging.error(traceback.format_exc())
        else:
            self.update_buffer(edit)

    def is_enabled(self):
        """Determine if this command is enabled or not
        """

        return is_code(self.view, lang='rust', ignore_comments=True)

    def on_failure(self, *args, **kwargs):
        """Called when callback return a failure or times out
        """

        self.pbar.terminate(status=self.pbar.Status.FAILURE)
        self.view.set_read_only(False)

    def prepare_data(self, data):
        """Prepare the returned data to overwrite our buffer
        """

        self.pbar.terminate()
        self.view.set_read_only(False)
        self.output = data['output']
        sublime.active_window().run_command(self.name())

    def update_buffer(self, edit):
        """Update and reload the buffer
        """

        code = self.view.substr(sublime.Region(0, self.view.size()))
        view = get_window_view(self.data['vid'])
        if code != self.output:
            region = sublime.Region(0, view.size())
            view.replace(edit, region, self.output)
            if get_settings(view, 'rust_format_on_save'):
                sublime.set_timeout(lambda: view.run_command('save'), 0)

        self.output = None
