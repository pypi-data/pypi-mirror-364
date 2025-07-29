from .Logger import logger
import sys
import atexit
import traceback
import pathlib


def show_html():
    html_path = pathlib.Path(sys.argv[0]).stem # no extension    
    logger.show(html_path)
    
def log_last_exception():    
    try:
        t = getattr(sys,'last_type') # not always defined. #https://docs.python.org/3/library/sys.html#sys.exc_info
        v = getattr(sys,'last_value')
        tb = getattr(sys,'last_traceback')
        _exp = traceback.format_exception(t,v,tb)
        formatted_lines = '\n'.join(_exp).replace("\\n","\n").replace("\\t","\t")        
        logger.log_pretext(formatted_lines)
    except AttributeError: 
        pass

atexit.register(show_html)
atexit.register(log_last_exception)