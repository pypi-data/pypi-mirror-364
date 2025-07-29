__author__ = 'chaoweichen26@gmail.com'

from bokger import logger
import numpy as np

def test_log_latex():
    logger.log_div('$$\sin^2(x) + \cos^2(x) = 1$$')

def test_log_json():
    logger.log({"a":1,"b":2,"c": [3,4]})
    logger.log([1,2,3])
    logger.log(np.array([1,2,3]))

    arr = np.arange(1,4)
    logger.log("arr", arr, f"{arr=}")    
    
    arr2d = np.array([[1,2,3],[4,5,6]])
    logger.log("arr2d",arr2d, f"{arr2d=}")

if __name__ == '__main__':
    test_log_json()