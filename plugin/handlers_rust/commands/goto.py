
# Copyright (C) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import sys
import shlex
import logging
import traceback
import subprocess

from commands.base import Command

PIPE = subprocess.PIPE


class Goto(Command):
    """Run racer
    """

    def __init__(self, callback, uid, vid, filename, settings):
        self.vid = vid
        self.filename = filename
        self.settings = settings
        super(Goto, self).__init__(callback, uid)

    def run(self):
        """Run the command
        """

        try:
            self.callback({
                'success': True,
                'goto': self.get_definitions(),
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

    def get_definitions(self):
        """Call racer and get back the definition data
        """

        matches = []
        args = shlex.split(
            '{0} -i tab-text find-definition {1} {2} {3} -'.format(
                self.settings.get('racer_binary_path', 'racer'),
                self.settings.get('row', 0) + 1,  # ST3 counts rows from 0
                self.settings.get('col', 0),
                os.path.dirname(self.filename)
            ), posix=os.name != 'nt'
        )
        env = os.environ.copy()
        rust_src_path = self.settings.get('rust_src_path')
        if rust_src_path is None or rust_src_path == '':
            rust_src_path = os.environ['RUST_SRC_PATH']

        env['RUST_SRC_PATH'] = rust_src_path
        read, write = os.pipe()
        try:
            os.write(write, self.settings['source'])
        except TypeError:
            os.write(write, self.settings['source'].encode())
        os.close(write)
        output = subprocess.check_output(
            args, stdin=read, cwd=os.getcwd(), env=env)
        if sys.version_info >= (3, 0):
            output = output.decode('utf8')

        if 'RUST_BACKTRACE' in output:
            raise Exception(output)

        for line in output.splitlines():
            if not line.startswith('MATCH'):
                continue

            _, elem, row, col, path, _, _ = line.split('\t')
            matches.append((path, int(row), int(col)))

        return matches
