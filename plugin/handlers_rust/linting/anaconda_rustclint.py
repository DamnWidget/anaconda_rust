
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

"""AnacondaRUST rustc lint wrapper
"""

import os
import sys
import shlex
import subprocess

from process import spawn

PIPE = subprocess.PIPE


class RustCLint(object):
    """RustCLint class for AnacondaRUST
    """

    def __init__(self, filename, settings):
        self.filename = filename
        self.settings = settings
        self.output = None

        self.execute()

    def execute(self):
        """Execute the linting process
        """

        args = shlex.split('rustc -Zparse-only {0}'.format(self.filename))
        proc = spawn(args, stdout=PIPE, stderr=PIPE, cwd=os.getcwd())
        _, self.output = proc.communicate()
        if sys.version_info >= (3, 0):
            self.output = self.output.decode('utf8')

    def parse_error(self):
        """Parse the output given by rustc -Zparse_only
        """

        errors = {'E': [], 'W': [], 'V': []}
        if self.output != '':
            split_lines = self.output.splitlines()
            for line in split_lines:
                if 'warning: the option `Z`' in line:
                    # ignore this line
                    continue



