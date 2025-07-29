
  
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
    return _lib.Incr_fn_main_2fcce0(ctx=ctx, _32449_input_EAG3JP=Length,_32451_input_IjkHqJ=LengthInput,_32453_input_TKM1Eb=SmoothingFactor,_32455_input_rodj36=FastLength,_32457_input_stdvv2=SlowLength).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def stc(self) -> float:
        return self.__inner._31526_stc()
  

    @property
    def macd(self) -> float:
        return self.__inner._31527_macd()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, Length: Optional[int] = None, LengthInput: Optional[int] = None, SmoothingFactor: Optional[float] = None, FastLength: Optional[int] = None, SlowLength: Optional[int] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_2fcce0(ctx, _32449_input_EAG3JP=Length,_32451_input_IjkHqJ=LengthInput,_32453_input_TKM1Eb=SmoothingFactor,_32455_input_rodj36=FastLength,_32457_input_stdvv2=SlowLength)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          