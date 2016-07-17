
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import subprocess

from anaconda_rust.anaconda_lib.helpers import get_settings, active_view

RACER_VERSION = None


def check_racer_version():
    """Check the installed racer version
    """

    global RACER_VERSION

    view = active_view()
    racer = get_settings(view, 'racer_binary_path', 'racer')
    if racer == '':
        racer = 'racer'

    env = os.environ.copy()
    rust_src_path = get_settings(view, 'rust_src_path')
    if rust_src_path is None or rust_src_path == '':
        rust_src_path = os.environ.get('RUST_SRC_PATH', '')

    env['RUST_SRC_PATH'] = rust_src_path

    try:
        data = subprocess.check_output([racer, '-V'], env=env)
        RACER_VERSION = tuple(int(i) for i in data.split()[1].split(b'.'))
    except Exception as error:
        print('Can\'t determine racer version: {}'.format(error))
