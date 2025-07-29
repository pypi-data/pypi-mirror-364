
  
from dataclasses import dataclass
from typing import Optional, Union, Literal, TypedDict, Any, Tuple, List
from datetime import datetime
from qpace import Ctx, Backtest
from qpace_suite import _lib
  
  

class MainAlert(TypedDict):
    time: datetime
    bar_index: int
    title: Optional[str]
    message: Optional[str]

class MainResultLocals(TypedDict):

    stc: List[float]
    

    macd: List[float]
    
    pass

class MainResult(TypedDict):
    alerts: List[MainAlert]
    locals: MainResultLocals


def main(ctx: Ctx, Length: Optional[int] = None, LengthInput: Optional[int] = None, SmoothingFactor: Optional[float] = None, FastLength: Optional[int] = None, SlowLength: Optional[int] = None) -> MainResult:
    """
`main() -> void`
    """
    return _lib.Incr_fn_main_dc2f01(ctx=ctx, _20773_input_sA8JvQ=Length,_20775_input_DMazOf=LengthInput,_20777_input_ZLR9PW=SmoothingFactor,_20779_input_pK6RJC=FastLength,_20781_input_S8DnkI=SlowLength).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def stc(self) -> float:
        return self.__inner._19850_stc()
  

    @property
    def macd(self) -> float:
        return self.__inner._19851_macd()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, Length: Optional[int] = None, LengthInput: Optional[int] = None, SmoothingFactor: Optional[float] = None, FastLength: Optional[int] = None, SlowLength: Optional[int] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_dc2f01(ctx, _20773_input_sA8JvQ=Length,_20775_input_DMazOf=LengthInput,_20777_input_ZLR9PW=SmoothingFactor,_20779_input_pK6RJC=FastLength,_20781_input_S8DnkI=SlowLength)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          