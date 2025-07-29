'''
can use decorator to log i/o 
'''
__author__ = "chaoweichen26@gmail.com"

from bokger import dec
from bokger import op_table
from time import sleep

@dec.log
def my_fn(num1 : int, num2 : int, num3 : int , num4 : int):
    sleep(0.1)
    return num1+num2+num3+num4

my_fn(1,2,num3=3, num4=4)

@dec.log
def fib(n):
    if n < 2: return 1
    else:
        return fib(n-1) + fib(n-2)

fib(4)

@dec.log
class MyModule:
    def __init__(self):
        self.var = 0

    def get(self):
        return self.var
    
    def set(self, v):
        self.var = v

m = MyModule()
m.set(123,), m.get()

rec = op_table.records
print(rec)
