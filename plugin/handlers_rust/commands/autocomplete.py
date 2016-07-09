
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

    def completions(self):
        """Call racer and get back a formated list of completions
        """

        completions = []

        args = shlex.split(
            '{0} -i tab-text complete-with-snippet {1} {2} {3} -'.format(
                self.settings.get('racer_binary_path', 'racer'),
                self.settings.get('row', 0) + 1,  # ST3 counts rows from 0
                self.settings.get('col', 0),
                os.path.dirname(self.filename)
            ), posix=os.name != 'nt'
        )
        env = os.environ.copy()
        rust_src_path = self.settings.get('rust_src_path')
        if rust_src_path is None or rust_src_path == '':
            rust_src_path = os.environ.get('RUST_SRC_PATH', '')

        env['RUST_SRC_PATH'] = rust_src_path
        kwargs = {
            'stdin': PIPE, 'stdout': PIPE, 'stderr': PIPE,
            'cwd': os.getcwd(), 'env': env
        }
        try:

            racer = spawn(args, **kwargs)
        except subprocess.CalledProcessError:
            new_env = []
            for elem in env:
                new_env.append(str(elem))
            racer = spawn(args, **kwargs)

        src = self.settings['source']
        if sys.version_info >= (3, 0):
            src = self.settings['source'].encode()

        output, error = racer.communicate(src)
        if sys.version_info >= (3, 0):
            output = output.decode('utf8')
            error = error.decode('utf8')

        if error != '':
            raise Exception(error)

        lguide = self._calculate_lguide(output)

        for line in output.splitlines():
            if not line.startswith('MATCH'):
                continue

            try:
                _, completion, snippet, _, _, _, _type, info = line.split('\t')
            except ValueError:
                # racer 1.2.10 added a new `doc` field
                _, completion, snippet, _, _, _, _type, info, doc = \
                    line.split('\t')

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
