
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

from lib import anaconda_handler

from .commands import RustFMT


class RustFMTHandler(anaconda_handler.AnacondaHandler):
    """Handle requests to execute rustfmt command from the JsonSever
    """

    __handler_type__ = 'rustfmt'

    def format(self, settings=None):
        """Run the rustfmt in a file
        """

        RustFMT(self.callback, self.uid, self.vid, settings)
