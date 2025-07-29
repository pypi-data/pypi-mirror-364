'''    
from bokger import logger
logger.log("example")
'''
from ._version import __version__

from .Logger import logger
from .OpTable import op_table

from . import _at_enter
from . import _at_exit
