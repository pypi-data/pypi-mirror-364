
  
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
    return _lib.Incr_fn_main_798c9a(ctx=ctx, _26662_input_1CcClN=ExpRate,_26664_input_RnQ8iI=InitialDistance,_26666_input_7SM4zE=WidthMultiplier).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def _initial(self) -> float:
        return self.__inner._25738__initial()
  

    @property
    def trend(self) -> int:
        return self.__inner._25739_trend()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, ExpRate: Optional[float] = None, InitialDistance: Optional[float] = None, WidthMultiplier: Optional[float] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_798c9a(ctx, _26662_input_1CcClN=ExpRate,_26664_input_RnQ8iI=InitialDistance,_26666_input_7SM4zE=WidthMultiplier)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          