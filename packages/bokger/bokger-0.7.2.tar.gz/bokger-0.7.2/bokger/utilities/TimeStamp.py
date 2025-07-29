from datetime import datetime as dt

_datetime_format = "%Y/%m/%d-%H:%M:%S"
_time_format = "%H:%M:%S"

def get_timestamp() -> dt: 
    ''' get current local time '''
    return dt.now()

def get_datetime_str() -> str:
    ''' get current local time in uniformed format '''
    now = get_timestamp()    
    return now.strftime(_datetime_format)

def get_timestamp_str() -> str:
    ''' get current local time in uniformed format '''
    now = get_timestamp()    
    return now.strftime(_time_format)
