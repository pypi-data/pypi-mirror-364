from .Database import _Database
import pandas as pd
import pickle
from datetime import datetime as dt
from pydecor import Decorated

def _repr(*args, **kwargs) -> str:
    _args = ', '.join([repr(a) for a in args])
    _kwargs = ', '.join([f'{k}={v}' for k, v in kwargs.items()])
    if _args and _kwargs:
        return _args + ', ' + _kwargs
    elif _args and not _kwargs:
        return _args
    elif not _args and _kwargs:
        return _kwargs
    else:
        return ""

class OpInfo:
    args = ()
    kwargs = {}
    op = None
    result = None
    started = 0
    ended = 0
    
    def __repr__(self):
        _module_method_name = self.op
        _args = _repr(*self.args, **self.kwargs)
        _msg = f"{_module_method_name}({_args}) -> {self.result}"
        _elapsed_sec = self.ended - self.started
        _elapsed_msg = "" if _elapsed_sec.seconds < 0.001 else f" # elapsed {_elapsed_sec} seconds"
        return _msg + _elapsed_msg
    
    def to_df(self) -> pd.DataFrame:
        df = pd.DataFrame(columns = ['args','kwargs','op','result','started','ended'],
                          dtype=object).astype(
                              {'started':'datetime64[ns]',
                               'ended':'datetime64[ns]', 
                               'op': str})
        df.loc[0] = {'args' : self.args,
                     'kwargs' : self.kwargs,
                     'op' : self.op,
                     'result' : self.result,
                     'started' : self.started,
                     'ended' : self.ended,
                     }
        return df
    
    
    def serialize(self):
        _s = OpInfo()
        _s.args = pickle.dumps(self.args)
        _s.kwargs = pickle.dumps(self.kwargs)
        _s.op = self.op
        _s.result = pickle.dumps(self.result)
        _s.started = self.started
        _s.ended = self.ended
        return _s

    @classmethod
    def deserialize(clz, opInfo):
        _ds = OpInfo()
        _ds.args = pickle.loads(opInfo.args)
        _ds.kwargs = pickle.loads(opInfo.kwargs)
        _ds.op = opInfo.op
        _ds.result = opInfo.result
        _ds.started = opInfo.started
        _ds.ended = opInfo.ended
        return _ds
        
    @classmethod
    def from_df(clz, df : pd.DataFrame, index):
        opInfo = OpInfo()
        opInfo.args = df
        for col in ['args','kwargs','op','result','started','ended']:
            v = df.at[index, col]
            setattr(opInfo,col,v)
        return opInfo

    @classmethod
    def from_Decorated(clz, dec : Decorated, started, ended):
        opInfo = OpInfo()    
        opInfo.args : tuple = dec.args
        opInfo.kwargs : dict = dec.kwargs
        opInfo.op : str = dec.wrapped.__qualname__
        opInfo.result : object = dec.result
        opInfo.started : dt = started
        opInfo.ended : dt = ended
        return opInfo

class OpTable(_Database):
    def __init__(self):
        super().__init__()
        self.table_class = OpInfo 
        self.table_name = OpInfo.__name__
        self._columns = [a for a in dir(OpInfo) if not a.startswith("__")]
    
    @property
    def columns(self):
        return self._columns
    
    def append(self, record):
        assert isinstance(record, self.table_class)
        df = record.serialize().to_df()        
        df.to_sql(self.table_name, self.conn, if_exists='append', index=False)

    @property
    def records(self):
        _df = pd.read_sql(f'select * from {self.table_name}', self.conn)
        _df.args = _df.args.apply(pickle.loads)
        _df.kwargs = _df.kwargs.apply(pickle.loads)
        _df.result = _df.result.apply(pickle.loads)
        return _df

op_table = OpTable()
