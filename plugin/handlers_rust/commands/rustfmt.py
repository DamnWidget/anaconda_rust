
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import sys
import shlex
import logging
import traceback
import subprocess

from commands.base import Command

from process import spawn

PIPE = subprocess.PIPE


class RustFMT(Command):
    """Run rustfmt in the given file
    """

    def __init__(self, callback, uid, vid, filename, settings):
        self.vid = vid
        self.filename = filename
        self.settings = settings
        super(RustFMT, self).__init__(callback, uid)

    def run(self):
        """Run the command
        """

        self.error = ''
        try:
            self.callback({
                'success': True,
                'output': self.rustfmt(),
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

    def rustfmt(self):
        """Run the rustfmt command in a file
        """

        args = shlex.split(
            '{0} --write-mode=plain --config-path {1} {2}'.format(
                self.settings.get('rustfmt_binary_path', 'rustfmt'),
                self.settings.get('config_path'),
                self.filename
            ),
            posix=os.name != 'nt')

        proc = spawn(args, stdout=PIPE, stderr=PIPE, cwd=os.getcwd())
        output, err = proc.communicate()
        if sys.version_info >= (3, 0):
            output = output.decode('utf8')
            err = err.decode('utf8')

        header = 'Using rustfmt config file '
        result = '\n'.join(
            [l for l in output.splitlines() if not l.startswith(header)])

        # delete temporary file
        if os.path.exists(self.filename):
            os.remove(self.filename)

        if err != '':
            self.error = err
            raise Exception(err)

        return result
