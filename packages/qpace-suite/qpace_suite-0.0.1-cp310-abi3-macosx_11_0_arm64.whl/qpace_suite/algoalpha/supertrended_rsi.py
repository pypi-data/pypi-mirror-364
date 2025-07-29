
  
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

    rsiValue: List[float]
    

    rsiMovingAverage: List[float]
    

    rsiSupertrend: List[float]
    

    trendDirection: List[int]
    
    pass

class MainResult(TypedDict):
    alerts: List[MainAlert]
    locals: MainResultLocals


def main(ctx: Ctx, RelativeStrengthIndexLength: Optional[int] = None, SmoothingLength: Optional[int] = None, RsiInputSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, IsSmoothed: Optional[bool] = None, MovingAverageLength: Optional[int] = None, MovingAverageType: Optional[str] = None, TrendFactor: Optional[float] = None, AverageTrueRangeLength: Optional[int] = None) -> MainResult:
    """
`main() -> void`
    """
    return _lib.Incr_fn_main_652aa2(ctx=ctx, _29599_input_sSItMD=RelativeStrengthIndexLength,_29601_input_DnS940=SmoothingLength,_29603_input_PQLDy2=RsiInputSource,_29605_input_CMchDY=IsSmoothed,_29607_input_xAla5d=MovingAverageLength,_29609_input_Y5eU4s=MovingAverageType,_29611_input_6rOr2d=TrendFactor,_29613_input_ygsxvI=AverageTrueRangeLength).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def rsiValue(self) -> float:
        return self.__inner._28697_rsiValue()
  

    @property
    def rsiMovingAverage(self) -> float:
        return self.__inner._28698_rsiMovingAverage()
  

    @property
    def rsiSupertrend(self) -> float:
        return self.__inner._28701_rsiSupertrend()
  

    @property
    def trendDirection(self) -> int:
        return self.__inner._28702_trendDirection()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, RelativeStrengthIndexLength: Optional[int] = None, SmoothingLength: Optional[int] = None, RsiInputSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, IsSmoothed: Optional[bool] = None, MovingAverageLength: Optional[int] = None, MovingAverageType: Optional[str] = None, TrendFactor: Optional[float] = None, AverageTrueRangeLength: Optional[int] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_652aa2(ctx, _29599_input_sSItMD=RelativeStrengthIndexLength,_29601_input_DnS940=SmoothingLength,_29603_input_PQLDy2=RsiInputSource,_29605_input_CMchDY=IsSmoothed,_29607_input_xAla5d=MovingAverageLength,_29609_input_Y5eU4s=MovingAverageType,_29611_input_6rOr2d=TrendFactor,_29613_input_ygsxvI=AverageTrueRangeLength)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          