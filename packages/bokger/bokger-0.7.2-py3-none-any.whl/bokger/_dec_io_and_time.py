__author__ = 'chaoweichen26@gmail.com'

from pydecor import Decorated
from typing import List, Callable
from datetime import datetime as dt
from .OpTable import OpInfo


def log(d: Decorated, subscribers : List[Callable]):
    _start = dt.now()
    _result = d(*d.args, **d.kwargs)
    _end = dt.now()
    record = OpInfo.from_Decorated(d, _start, _end)
    
    for _log in subscribers:
        _log(record)
    
    return _result # = d.result

