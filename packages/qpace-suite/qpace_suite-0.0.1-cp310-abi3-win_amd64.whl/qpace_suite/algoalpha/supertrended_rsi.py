
  
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
    return _lib.Incr_fn_main_a15c68(ctx=ctx, _20842_input_AYm8gA=RelativeStrengthIndexLength,_20844_input_V0RTHQ=SmoothingLength,_20846_input_JvSenk=RsiInputSource,_20848_input_DKtuSx=IsSmoothed,_20850_input_lumDCG=MovingAverageLength,_20852_input_KZ5FXn=MovingAverageType,_20854_input_0vOccU=TrendFactor,_20856_input_mi0CFT=AverageTrueRangeLength).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def rsiValue(self) -> float:
        return self.__inner._19940_rsiValue()
  

    @property
    def rsiMovingAverage(self) -> float:
        return self.__inner._19941_rsiMovingAverage()
  

    @property
    def rsiSupertrend(self) -> float:
        return self.__inner._19944_rsiSupertrend()
  

    @property
    def trendDirection(self) -> int:
        return self.__inner._19945_trendDirection()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, RelativeStrengthIndexLength: Optional[int] = None, SmoothingLength: Optional[int] = None, RsiInputSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, IsSmoothed: Optional[bool] = None, MovingAverageLength: Optional[int] = None, MovingAverageType: Optional[str] = None, TrendFactor: Optional[float] = None, AverageTrueRangeLength: Optional[int] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_a15c68(ctx, _20842_input_AYm8gA=RelativeStrengthIndexLength,_20844_input_V0RTHQ=SmoothingLength,_20846_input_JvSenk=RsiInputSource,_20848_input_DKtuSx=IsSmoothed,_20850_input_lumDCG=MovingAverageLength,_20852_input_KZ5FXn=MovingAverageType,_20854_input_0vOccU=TrendFactor,_20856_input_mi0CFT=AverageTrueRangeLength)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          