__author__ = 'chaoweichen26@gmail.com'

from bokger import logger

def add(a,b): return a+b

class Adder:
    def add(self, a, b):
        return a+b
    
logger.log_source(add)
logger.log_source(Adder)