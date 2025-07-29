'''
can monkey patch
'''

from bokger import logger
print = logger.log

def test_monkey_patch_print():
    print(f"hello world")

