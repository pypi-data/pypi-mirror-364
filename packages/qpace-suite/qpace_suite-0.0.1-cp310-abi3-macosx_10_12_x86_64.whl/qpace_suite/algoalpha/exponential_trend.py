
  
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

    _initial: List[float]
    

    trend: List[int]
    
    pass

class MainResult(TypedDict):
    alerts: List[MainAlert]
    locals: MainResultLocals


def main(ctx: Ctx, ExpRate: Optional[float] = None, InitialDistance: Optional[float] = None, WidthMultiplier: Optional[float] = None) -> MainResult:
    """
`main() -> void`
    """
    return _lib.Incr_fn_main_380c5a(ctx=ctx, _23743_input_6q91ag=ExpRate,_23745_input_NmDkoL=InitialDistance,_23747_input_iPKQDV=WidthMultiplier).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def _initial(self) -> float:
        return self.__inner._22819__initial()
  

    @property
    def trend(self) -> int:
        return self.__inner._22820_trend()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, ExpRate: Optional[float] = None, InitialDistance: Optional[float] = None, WidthMultiplier: Optional[float] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_380c5a(ctx, _23743_input_6q91ag=ExpRate,_23745_input_NmDkoL=InitialDistance,_23747_input_iPKQDV=WidthMultiplier)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          