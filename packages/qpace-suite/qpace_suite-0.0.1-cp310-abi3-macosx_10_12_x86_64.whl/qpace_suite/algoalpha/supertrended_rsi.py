
  
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
    return _lib.Incr_fn_main_bd878b(ctx=ctx, _23761_input_BAYEeF=RelativeStrengthIndexLength,_23763_input_bW8rhI=SmoothingLength,_23765_input_rQ5vbG=RsiInputSource,_23767_input_ULzF7T=IsSmoothed,_23769_input_rAL7rC=MovingAverageLength,_23771_input_vfpay5=MovingAverageType,_23773_input_kD6ZHW=TrendFactor,_23775_input_Ye3DMc=AverageTrueRangeLength).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def rsiValue(self) -> float:
        return self.__inner._22859_rsiValue()
  

    @property
    def rsiMovingAverage(self) -> float:
        return self.__inner._22860_rsiMovingAverage()
  

    @property
    def rsiSupertrend(self) -> float:
        return self.__inner._22863_rsiSupertrend()
  

    @property
    def trendDirection(self) -> int:
        return self.__inner._22864_trendDirection()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, RelativeStrengthIndexLength: Optional[int] = None, SmoothingLength: Optional[int] = None, RsiInputSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, IsSmoothed: Optional[bool] = None, MovingAverageLength: Optional[int] = None, MovingAverageType: Optional[str] = None, TrendFactor: Optional[float] = None, AverageTrueRangeLength: Optional[int] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_bd878b(ctx, _23761_input_BAYEeF=RelativeStrengthIndexLength,_23763_input_bW8rhI=SmoothingLength,_23765_input_rQ5vbG=RsiInputSource,_23767_input_ULzF7T=IsSmoothed,_23769_input_rAL7rC=MovingAverageLength,_23771_input_vfpay5=MovingAverageType,_23773_input_kD6ZHW=TrendFactor,_23775_input_Ye3DMc=AverageTrueRangeLength)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          