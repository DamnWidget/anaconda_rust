
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

ANACONDA_PLUGIN_AVAILABLE = False
try:
    from anaconda.commands import doc
    from anaconda.anaconda_lib.worker import Worker
    from anaconda.anaconda_lib.helpers import is_code
    from anaconda.listeners import linting, completion
    from anaconda.anaconda_lib.callback import Callback
    from anaconda.anaconda_lib.jediusages import JediUsages
    from anaconda.version import version as anaconda_version
    from anaconda.anaconda_lib.progress_bar import ProgressBar
    from anaconda.anaconda_lib.helpers import prepare_send_data
    from anaconda.anaconda_lib import helpers as anaconda_helpers
    from anaconda.anaconda_lib.linting import sublime as anaconda_sublime
except ImportError:
    try:
        from Anaconda.commands import doc
        from Anaconda.anaconda_lib.worker import Worker
        from Anaconda.anaconda_lib.helpers import is_code
        from Anaconda.listeners import linting, completion
        from Anaconda.anaconda_lib.callback import Callback
        from Anaconda.anaconda_lib.jediusages import JediUsages
        from Anaconda.version import version as anaconda_version
        from Anaconda.anaconda_lib.progress_bar import ProgressBar
        from Anaconda.anaconda_lib.helpers import prepare_send_data
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
        'anaconda_version', 'linting', 'completion', 'anaconda_helpers',
        'prepare_send_data', 'JediUsages', 'doc'
    ]
