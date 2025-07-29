import sys

def _get_caller_info(caller: str):
    _frame = sys._getframe()
    
    while _frame:        
        if caller in _frame.f_code.co_filename:
            break
        else:
            _frame = _frame.f_back
    if _frame is None:
        return {'__author__': None, '__doc__': None}
    else:
        caller_f_code = _frame.f_code
        
        caller_info = {k:v for k, v in zip(caller_f_code.co_names, caller_f_code.co_consts)}
        author = caller_info.get('__author__', None)
        doc = caller_info.get('__doc__', None)
        return {'__author__': author, '__doc__': doc}
