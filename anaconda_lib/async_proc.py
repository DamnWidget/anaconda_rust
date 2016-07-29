
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import threading
import subprocess

PIPE = subprocess.PIPE


class AsyncProc(threading.Thread):
    """
    AsyncProc is just a fine wrapper around subprocess.Popen using threads
    to non block on wait and be able to stream output in realtime
    """

    class Status:
        NONE = None
        RUNNING = 'running'
        DONE = 'done'
        FAILED = 'fail'
        TIMED_OUT = 'timed_out'

    def __init__(self, callback, writer, *args, **kwargs):
        threading.Thread.__init__(self)
        self.exit = False
        self.callbak = callback
        self.popen_args = args

        if 'cwd' not in kwargs:
            kwargs['cwd'] = os.getcwd()

        if os.name == 'nt':
            kwargs['startupinfo'] = self.startupinfo

        self.popen_kwargs = kwargs

    @property
    def startupinfo(self):
        """Return back the startupinfo config for Windows
        """

        sinfo = subprocess.STARTUPINFO()
        sinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        return sinfo

    def run(self):
        """Run this AsyncProc
        """

        self.proc = subprocess.Popen(args, stdout=PIPE, sterr=PIPE, **kwargs)

