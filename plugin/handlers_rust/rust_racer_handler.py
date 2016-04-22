
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

from lib import anaconda_handler

from .commands import AutoComplete


class RacerHandler(anaconda_handler.AnacondaHandler):
    """Handle requests to execute racer related command to the JsonSever
    """

    __handler_type__ = 'racer'

    def autocomplete(self, filename=None, settings=None):
        """Call autocomplete
        """

        AutoComplete(self.callback, self.uid, self.vid, filename, settings)
