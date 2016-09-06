
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
        '^(?P<file>.+?):(?P<line>\\d+):(?P<col>\\d+):\\s+'
        '(?P<line_to>\\d+):(?P<col_to>\\d+)\\s'
        '(?:(?P<error>(error|fatal error))|(?P<warning>warning)|'
        '(?P<info>note|help)):\\s+(?P<message>.+)',
        re.MULTILINE | re.UNICODE
    )

    # regexp groups to parse rustc 1.13.x output
    _regexp_1_13 = re.compile(
        '^(?:(?P<error>(error|fatal error))|(?P<warning>warning)|'
        '(?P<info>note|help)):\\s+(?P<message>.+)\\s+'
        ' --> (?P<file>.+?):(?P<line>\\d+):(?P<col>\\d+)'
    )

    def __init__(self, filename, settings):
        self.filename = filename
        self.settings = settings
        self.output = None

        self.execute()

    def execute(self):
        """Execute the linting process
        """

        current_dir = os.getcwd()
        os.chdir(os.path.dirname(self.filename))
        args = shlex.split('{0} -Zparse-only {1}'.format(
            self.settings.get('rustc_binary_path', 'rustc'),
            os.path.basename(self.filename)), posix=os.name != 'nt'
        )
        proc = spawn(args, stdout=PIPE, stderr=PIPE, cwd=os.getcwd())
        _, self.output = proc.communicate()
        if sys.version_info >= (3, 0):
            self.output = self.output.decode('utf8')

        os.chdir(current_dir)

    def parse_errors(self):
        """Parse the output given by rustc -Zparse_only
        """

        errors = {'E': [], 'W': [], 'V': []}
        if self.output != '':
            for match in self._version_regex:
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

    def _infer_severity(self, match):
        """Infer the error severity from the result match
        """

        _severity = 'error'
        _type_dict = {'error': 'E', 'warning': 'W', 'info': 'V'}
        if match['warning'] is not None:
            _severity = 'warning'
        elif match['info'] is not None:
            _severity = 'info'

        return _severity, _type_dict[_severity]

    @property
    def _version_regex(self):
        """Execute the right regexp.finditer depenging on rustc version
        """

        r = self.settings.get('rustc_binary_path', 'rustc')
        args = shlex.split('{0} --version'.format(r), posix=os.name != 'nt')
        p = spawn(args, stdout=PIPE, stderr=PIPE)
        out, _ = p.communicate()
        if sys.version_info >= (3,):
            out = out.decode('utf8')

        if 'rustc' not in out:
            return []

        v = tuple(int(i) for i in out.split(' ')[1].split('-')[0].split('.'))
        if v >= (1, 13):
            return self._regexp_1_13.finditer(self.output)

        return self._regexp.finditer(self.output)
