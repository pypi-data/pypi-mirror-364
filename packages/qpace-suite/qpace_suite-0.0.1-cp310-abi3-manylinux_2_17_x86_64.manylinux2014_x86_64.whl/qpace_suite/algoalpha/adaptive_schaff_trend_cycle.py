
  
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
    return _lib.Incr_fn_main_f0a02f(ctx=ctx, _26611_input_pYjAdQ=Length,_26613_input_5cqy37=LengthInput,_26615_input_vDimLp=SmoothingFactor,_26617_input_KkTq5t=FastLength,_26619_input_cC0wdm=SlowLength).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def stc(self) -> float:
        return self.__inner._25688_stc()
  

    @property
    def macd(self) -> float:
        return self.__inner._25689_macd()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, Length: Optional[int] = None, LengthInput: Optional[int] = None, SmoothingFactor: Optional[float] = None, FastLength: Optional[int] = None, SlowLength: Optional[int] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_f0a02f(ctx, _26611_input_pYjAdQ=Length,_26613_input_5cqy37=LengthInput,_26615_input_vDimLp=SmoothingFactor,_26617_input_KkTq5t=FastLength,_26619_input_cC0wdm=SlowLength)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          