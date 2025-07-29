
  
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

    customRSI: List[float]
    
    pass

class MainResult(TypedDict):
    alerts: List[MainAlert]
    locals: MainResultLocals


def main(ctx: Ctx, OscPeriod: Optional[int] = None) -> MainResult:
    """
`main() -> void`
    """
    return _lib.Incr_fn_main_ae03c0(ctx=ctx, _20801_input_XQvyCW=OscPeriod).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def customRSI(self) -> float:
        return self.__inner._19860_customRSI()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, OscPeriod: Optional[int] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_ae03c0(ctx, _20801_input_XQvyCW=OscPeriod)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          