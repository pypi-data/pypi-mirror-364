"""
Teamly API Wrapper
~~~~~~~~~~~~~~~~~~~

A basic wrapper for the Teamly API.

:copyright: (c) 2025 Fatih Kuloglu
:license: MIT, see LICENSE for more details.

"""

__title__ = 'teamly'
__author__ = 'MrFatihLD'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2025 Fatih Kuloglu'
__version__ = '0.1.0a'

from . import (
    abc as abc,
    utils as utils
)
from .announcement import *
from .blog import *
from .cache import *
from .channel import *
from .client import *
from .color import *
from .embed import *
from .enums import *
from .gateway import *
from .http import *
from .member import *
from .message import *
from .reaction import *
from .state import *
from .team import *
from .todo import *
from .user import *
from .logging import setup_logging, enable_debug #noqa: F401 <- ignoring unused import warning

#hide debug logs by default
setup_logging(False)
