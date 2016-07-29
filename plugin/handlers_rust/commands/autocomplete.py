
# Copyright (C) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import logging
import traceback

from ..rust_anaconda.bridge import Complete
from commands.base import Command


class AutoComplete(Command):
    """Run racer
    """

    def __init__(self, callback, uid, vid, filename, settings):
        self.vid = vid
        self.path = os.path.dirname(filename)
        self.settings = settings
        super(AutoComplete, self).__init__(callback, uid)

    def run(self):
        """Run the command
        """

        try:
            src = self.settings.get('source', b'')
            row = self.settings.get('row', 1)
            col = self.settings.get('col', 1)
            with Complete(src, self.path, row, col) as result:
                completions = []
                lguide = self._calculate_lguide(result)
                for c in result:
                    completions.append((
                        '{0}{1} {2} {3}'.format(
                            c['match'], ' ' * (lguide - len(c['match'])),
                            c['mtype'].lower(), c['ctx']
                        ), c['snippet']
                    ))

                self.callback({
                    'success': True,
                    'completions': completions,
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

    def _calculate_lguide(self, completions):
        """Calculate the max string for components and return it back
        """

        lguide = 0
        for completion in completions:
            comp_string = completion['snippet']
            lguide = max(lguide, len(comp_string))

        return lguide
