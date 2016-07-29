
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

from lib import anaconda_handler

from .commands import Compile, CompilationError


class RustAnacondaHandler(anaconda_handler.AnacondaHandler):
    """Handle requests to compile rust-anaconda
    """

    __handler_type__ = 'rust_anaconda'

    def prepare(self, version, settings):
        """Prepare the rust-anaconda environment if needed
        """

        try:
            compiler = Compile(version, settings)
            self.callback({
                'success': True,
                'msg': compiler.compile(),
                'uid': self.uid,
                'vid': self.vid
            })
        except CompilationError as error:
            self.callback({
                'success': False,
                'error': error,
                'uid': self.uid,
                'vid': self.vid
            })
