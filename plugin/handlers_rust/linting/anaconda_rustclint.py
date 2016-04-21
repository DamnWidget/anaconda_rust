
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

"""AnacondaRUST rustc lint wrapper
"""

import os
import re
import sys
import shlex
import subprocess

from process import spawn

PIPE = subprocess.PIPE


class RustCLint(object):
    """RustCLint class for AnacondaRUST
    """

    # regexp groups to parse output
    _regexp = re.compile(
        r'^(?P<file>.+?):(?P<line>\\d+):(?P<col>\\d+):\\s+'
        r'(?P<line_to>\\d+):(?P<col_to>\\d+)\\s'
        r'(?:(?P<error>(error|fatal error))|(?P<warning>warning)|'
        r'(?P<info>note|help)):\\s+(?P<message>.+)'
    )


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
            for match in self._regexp.finditer(self.output):
                dict_match = match.groupdict()
                error_severity, error_type = self._infer_severity(dict_match)
                errors[error_type].append({
                    'line': dict_match['line'],
                    'offset': dict_match['col'],
                    'raw_message': dict_match['message'],
                    'code': 0,
                    'message': '[{0}] rustc ({1}): {2}'.format(
                        error_type, error_severity, dict_match['message']
                    )
                })

        return errors
