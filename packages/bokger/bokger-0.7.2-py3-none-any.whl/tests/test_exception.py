__author__ = 'chaoweichen26@gmail.com'

from bokger import dec

@dec.log
def decrement(n):
    if n<0:
        raise ValueError("intends to raise exception")
    return decrement(n-1)

def test_log_exception():
    decrement(1)
