
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import logging
import traceback

from ..rust_anaconda.bridge import Format
from commands.base import Command


class RustFMT(Command):
    """Run rustfmt in the given file
    """

    def __init__(self, callback, uid, vid, settings):
        self.vid = vid
        self.settings = settings
        super(RustFMT, self).__init__(callback, uid)

    def run(self):
        """Run the command
        """

        self.error = ''
        try:
            src = self.settings.get('source', b'')
            config_path = self.setting.get('config_path', b'')
            with Format(src, config_path) as fmt:
                self.callback({
                    'success': True,
                    'output': fmt,
                    'uid': self.uid,
                    'vid': self.vid
                })
        except:
            logging.error(self.error)
            trback = traceback.format_exc()
            logging.debug(trback)
            logging.debug('Settings: {0}'.format(self.settings))
            print(trback)
            self.callback({
                'success': False,
                'error': self.error,
                'uid': self.uid,
                'vid': self.vid
            })
