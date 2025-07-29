
  
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
    return _lib.Incr_fn_main_d7ce8a(ctx=ctx, _26680_input_VSAlaH=RelativeStrengthIndexLength,_26682_input_RqqNTJ=SmoothingLength,_26684_input_Zrb7cN=RsiInputSource,_26686_input_j2OE1E=IsSmoothed,_26688_input_olas2o=MovingAverageLength,_26690_input_F1INOq=MovingAverageType,_26692_input_talz6r=TrendFactor,_26694_input_kuueNl=AverageTrueRangeLength).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def rsiValue(self) -> float:
        return self.__inner._25778_rsiValue()
  

    @property
    def rsiMovingAverage(self) -> float:
        return self.__inner._25779_rsiMovingAverage()
  

    @property
    def rsiSupertrend(self) -> float:
        return self.__inner._25782_rsiSupertrend()
  

    @property
    def trendDirection(self) -> int:
        return self.__inner._25783_trendDirection()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, RelativeStrengthIndexLength: Optional[int] = None, SmoothingLength: Optional[int] = None, RsiInputSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, IsSmoothed: Optional[bool] = None, MovingAverageLength: Optional[int] = None, MovingAverageType: Optional[str] = None, TrendFactor: Optional[float] = None, AverageTrueRangeLength: Optional[int] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_d7ce8a(ctx, _26680_input_VSAlaH=RelativeStrengthIndexLength,_26682_input_RqqNTJ=SmoothingLength,_26684_input_Zrb7cN=RsiInputSource,_26686_input_j2OE1E=IsSmoothed,_26688_input_olas2o=MovingAverageLength,_26690_input_F1INOq=MovingAverageType,_26692_input_talz6r=TrendFactor,_26694_input_kuueNl=AverageTrueRangeLength)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          