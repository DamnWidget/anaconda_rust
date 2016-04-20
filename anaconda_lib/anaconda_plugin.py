
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

ANACONDA_PLUGIN_AVAILABLE = False
try:
    from anaconda.listeners import linting
    from anaconda.anaconda_lib.worker import Worker
    from anaconda.anaconda_lib.helpers import is_code
    from anaconda.anaconda_lib.callback import Callback
    from anaconda.version import version as anaconda_version
    from anaconda.anaconda_lib.progress_bar import ProgressBar
    from anaconda.anaconda_lib import helpers as anaconda_helpers
    from anaconda.anaconda_lib.linting import sublime as anaconda_sublime
except ImportError:
    try:
        from Anaconda.listeners import linting
        from Anaconda.anaconda_lib.worker import Worker
        from Anaconda.anaconda_lib.helpers import is_code
        from Anaconda.anaconda_lib.callback import Callback
        from Anaconda.version import version as anaconda_version
        from Anaconda.anaconda_lib.progress_bar import ProgressBar
        from Anaconda.anaconda_lib import helpers as anaconda_helpers
        from Anaconda.anaconda_lib.linting import sublime as anaconda_sublime
    except ImportError as error:
        print(str(error))
        raise RuntimeError('Anaconda plugin is not installed!')
    else:
        ANACONDA_PLUGIN_AVAILABLE = True
else:
    ANACONDA_PLUGIN_AVAILABLE = True


__all__ = ['ANACONDA_PLUGIN_AVAILABLE']

if ANACONDA_PLUGIN_AVAILABLE:
    __all__ += [
        'Worker', 'Callback', 'ProgressBar', 'anaconda_sublime', 'is_code',
        'anaconda_version', 'linting', 'anaconda_helpers'
    ]
