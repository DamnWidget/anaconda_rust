
# Copyright (C) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import logging
import traceback

from ..rust_anaconda.bridge import Documentation
from commands.base import Command


class Doc(Command):
    """Run racer
    """

    def __init__(self, callback, uid, vid, filename, settings):
        self.vid = vid
        self.path = os.path.dirname(filename)
        self.settings = settings
        super(Doc, self).__init__(callback, uid)

    def run(self):
        """Run the command
        """

        try:
            src = self.settings.get('source', b'')
            row = self.settings.get('row', 1)
            col = self.settings.get('col', 1)
            with Documentation(src, self.path, row, col) as doc:
                self.callback({
                    'success': True,
                    'doc': doc,
                    'uid': self.uid,
                    'vid': self.vid
                })
        except Exception as error:
            logging.error('The underlying racer tool raised an exception')
            logging.error(error)
            logging.debug(traceback.format_exc())

            self.callback({
                'success': False,
                'error': str(error),
                'uid': self.uid,
                'vid': self.vid
            })
