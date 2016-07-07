
# Copyright (C) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import ast
import sys
import shlex
import logging
import traceback
import subprocess

from commands.base import Command

PIPE = subprocess.PIPE


class Doc(Command):
    """Run racer
    """

    def __init__(self, callback, uid, vid, filename, settings):
        self.vid = vid
        self.filename = filename
        self.settings = settings
        super(Doc, self).__init__(callback, uid)

    def run(self):
        """Run the command
        """

        try:
            self.callback({
                'success': True,
                'doc': self.doc(),
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

    def doc(self):
        """Call racer and get back documentation (only on racer >= 1.2.10)
        """

        args = shlex.split(
            '{0} -i tab-text complete-with-snippet {1} {2} {3} -'.format(
                self.settings.get('racer_binary_path', 'racer'),
                self.settings.get('row', 0) + 1,  # ST3 counts rows from 0
                self.settings.get('col', 0),
                self.filename
            ), posix=os.name != 'nt'
        )
        env = os.environ.copy()
        rust_src_path = self.settings.get('rust_src_path')
        if rust_src_path is None or rust_src_path == '':
            rust_src_path = os.environ.get('RUST_SRC_PATH', '')

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

            try:
                # racer 1.2.10 added a new `doc` field
                _, _, _, _, _, _, _, info, doc = line.split('\t')
            except ValueError:
                raise RuntimeError('doc is available in racer >= 1.2.10 only')

            if not doc:
                doc = info

            if doc == "\"\"":
                doc = ""

            if doc == '':
                return doc

            return ast.literal_eval(doc)
