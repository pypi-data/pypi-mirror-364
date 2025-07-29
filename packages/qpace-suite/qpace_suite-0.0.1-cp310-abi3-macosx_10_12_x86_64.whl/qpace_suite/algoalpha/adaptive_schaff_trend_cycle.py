
  
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
    return _lib.Incr_fn_main_b6bc0f(ctx=ctx, _23692_input_W08TIo=Length,_23694_input_5Vej1O=LengthInput,_23696_input_Wv4Upn=SmoothingFactor,_23698_input_2gRnbj=FastLength,_23700_input_tK7guk=SlowLength).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def stc(self) -> float:
        return self.__inner._22769_stc()
  

    @property
    def macd(self) -> float:
        return self.__inner._22770_macd()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, Length: Optional[int] = None, LengthInput: Optional[int] = None, SmoothingFactor: Optional[float] = None, FastLength: Optional[int] = None, SlowLength: Optional[int] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_b6bc0f(ctx, _23692_input_W08TIo=Length,_23694_input_5Vej1O=LengthInput,_23696_input_Wv4Upn=SmoothingFactor,_23698_input_2gRnbj=FastLength,_23700_input_tK7guk=SlowLength)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          