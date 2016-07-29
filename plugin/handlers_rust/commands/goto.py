
# Copyright (C) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import logging
import traceback

from ..rust_anaconda.bridge import Definitions
from commands.base import Command


class Goto(Command):
    """Run racer
    """

    def __init__(self, callback, uid, vid, filename, settings):
        self.vid = vid
        self.path = os.path.dirname(filename)
        self.settings = settings
        super(Goto, self).__init__(callback, uid)

    def run(self):
        """Run the command
        """

        try:
            src = self.settings.get('source', b'')
            row = self.settings.get('row', 1)
            col = self.settings.get('col', 1)
            with Definitions(src, self.path, row, col) as defs:
                self.callback({
                    'success': True,
                    'goto': [(d['path'], d['row'], d['col']) for d in defs],
                    'uid': self.uid,
                    'vid': self.vid
                })
        except Exception as error:
            logging.error(error)
            logging.debug(traceback.format_exc().splitlines())

            self.callback({
                'success': False,
                'error': str(error),
                'uid': self.uid,
                'vid': self.vid
            })
