
# Copyright (C) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
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


class AutoComplete(Command):
    """Run racer
    """

    def __init__(self, callback, uid, vid, filename, settings):
        self.vid = vid
        self.filename = filename
        self.settings = settings
        super(AutoComplete, self).__init__(callback, uid)

    def run(self):
        """Run the command
        """

        try:
            self.callback({
                'success': True,
                'completions': self.completions(),
                'uid': self.uid,
                'vid': self.vid
            })
        except:
            logging.error('The underlying racer tool raised an exception')
            logging.debug(traceback.format_exc().splitlines())
            logging.error(self.error)

            self.callback({
                'success': False,
                'error': str(self.error),
                'uid': self.uid,
                'vid': self.vid
            })

    def completions(self):
        """Call racer and get back a formated list of completions
        """

        completions = []
        args = shlex.split(
            '{0} -i tab-text complete-with-snippet {1} {2} {3}'.format(
                self.settings.get('racer_binary_path', 'racer'),
                self.settings.get('row', 0) + 1,  # ST3 counts rows from 0
                self.settings.get('col', 0),
                self.filename
            ), posix=os.name != 'nt'
        )
        env = os.environ.copy()
        rust_src_path = self.settings.get('rust_src_path')
        if rust_src_path is None or rust_src_path == '':
            rust_src_path = os.environ['RUST_SRC_PATH']

        env['RUST_SRC_PATH'] = rust_src_path
        proc = spawn(args, stdout=PIPE, stderr=PIPE, cwd=os.getcwd(), env=env)
        output, err = proc.communicate()
        if sys.version_info >= (3, 0):
            output = output.decode('utf8')
            err = err.decode('utf8')

        # delete temporary file
        if os.path.exists(self.filename):
            os.remove(self.filename)

        if err != '':
            self.error = err
            raise Exception(err)

        lguide = self._calculate_lguide(output)

        for line in output.splitlines():
            if not line.startswith('MATCH'):
                continue

            _, completion, snippet, _, _, _, _type, info = line.split('\t')
            completions.append((
                '{0}{1} {2} {3}'.format(
                    completion, ' ' * (lguide - len(completion)),
                    _type[0].lower(), info
                ), snippet
            ))

        return completions

    def _calculate_lguide(self, output):
        """Calculate the max string for components and return it back
        """

        lguide = 0
        for line in output.splitlines():
            if not line.startswith('MATCH'):
                continue

            comp_string = line.split('\t')[1]
            lguide = max(lguide, len(comp_string))

        return lguide
