
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import logging
import traceback

from commands.base import Command


class RustCLinter(Command):
    """Run rustc -Zparse-only and return back results
    """

    def __init__(self, callback, uid, vid, linter, settings, code, filename):
        self.vid = vid
        self.code = code
        self.linter = linter
        self.settings = settings
        self.filename = filename
        super(RustCLinter, self).__init__(callback, uid)

    def run(self):
        """Run the command
        """

        try:
            self.callback({
                'success': True,
                'errors': self.linter(
                    self.filename, self.settings).parse_errors(),
                'uid': self.uid,
                'vid': self.vid
            })
        except Exception as error:
            logging.error(error)
            trback = traceback.format_exc()
            logging.debug(trback)
            print(trback)
            self.callback({
                'success': False,
                'error': error,
                'uid': self.uid,
                'vid': self.vid
            })
