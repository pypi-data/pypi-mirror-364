__author__ = 'chaoweichen26@gmail.com'

from pydecor import instead
from bokger import _dec_io_and_time, logger, op_table

log = instead(_dec_io_and_time.log, subscribers=[logger.log, op_table.append])

