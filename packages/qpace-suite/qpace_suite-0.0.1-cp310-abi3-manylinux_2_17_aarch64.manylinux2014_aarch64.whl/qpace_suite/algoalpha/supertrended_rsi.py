
  
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
    return _lib.Incr_fn_main_3bd6e4(ctx=ctx, _32518_input_FQDTyw=RelativeStrengthIndexLength,_32520_input_1wF5Kh=SmoothingLength,_32522_input_w0wjtN=RsiInputSource,_32524_input_VQukZK=IsSmoothed,_32526_input_iLtR2z=MovingAverageLength,_32528_input_brM88j=MovingAverageType,_32530_input_j5L2Xm=TrendFactor,_32532_input_UetLcE=AverageTrueRangeLength).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def rsiValue(self) -> float:
        return self.__inner._31616_rsiValue()
  

    @property
    def rsiMovingAverage(self) -> float:
        return self.__inner._31617_rsiMovingAverage()
  

    @property
    def rsiSupertrend(self) -> float:
        return self.__inner._31620_rsiSupertrend()
  

    @property
    def trendDirection(self) -> int:
        return self.__inner._31621_trendDirection()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, RelativeStrengthIndexLength: Optional[int] = None, SmoothingLength: Optional[int] = None, RsiInputSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, IsSmoothed: Optional[bool] = None, MovingAverageLength: Optional[int] = None, MovingAverageType: Optional[str] = None, TrendFactor: Optional[float] = None, AverageTrueRangeLength: Optional[int] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_3bd6e4(ctx, _32518_input_FQDTyw=RelativeStrengthIndexLength,_32520_input_1wF5Kh=SmoothingLength,_32522_input_w0wjtN=RsiInputSource,_32524_input_VQukZK=IsSmoothed,_32526_input_iLtR2z=MovingAverageLength,_32528_input_brM88j=MovingAverageType,_32530_input_j5L2Xm=TrendFactor,_32532_input_UetLcE=AverageTrueRangeLength)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          