
  
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

    yhat_close: List[float]
    

    yhat_high: List[float]
    

    yhat_low: List[float]
    

    yhat: List[float]
    

    ktr: List[float]
    

    upper_near: List[float]
    

    upper_far: List[float]
    

    upper_avg: List[float]
    

    lower_near: List[float]
    

    lower_far: List[float]
    

    lower_avg: List[float]
    
    pass

class MainResult(TypedDict):
    alerts: List[MainAlert]
    locals: MainResultLocals


def main(ctx: Ctx, H: Optional[int] = None, Alpha: Optional[float] = None, X0: Optional[int] = None, AtrLength: Optional[int] = None, NearFactor: Optional[float] = None, FarFactor: Optional[float] = None) -> MainResult:
    """
`main() -> void`
    """
    return _lib.Incr_fn_main_a0ed1d(ctx=ctx, _30246_input_8c5Jms=H,_30248_input_ryj1d6=Alpha,_30250_input_23yvh7=X0,_30255_input_HQSy15=AtrLength,_30258_input_DtdkCx=NearFactor,_30260_input_iRYo4G=FarFactor).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def yhat_close(self) -> float:
        return self.__inner._29369_yhat_close()
  

    @property
    def yhat_high(self) -> float:
        return self.__inner._29370_yhat_high()
  

    @property
    def yhat_low(self) -> float:
        return self.__inner._29371_yhat_low()
  

    @property
    def yhat(self) -> float:
        return self.__inner._29372_yhat()
  

    @property
    def ktr(self) -> float:
        return self.__inner._29373_ktr()
  

    @property
    def upper_near(self) -> float:
        return self.__inner._29383_upper_near()
  

    @property
    def upper_far(self) -> float:
        return self.__inner._29384_upper_far()
  

    @property
    def upper_avg(self) -> float:
        return self.__inner._29385_upper_avg()
  

    @property
    def lower_near(self) -> float:
        return self.__inner._29386_lower_near()
  

    @property
    def lower_far(self) -> float:
        return self.__inner._29387_lower_far()
  

    @property
    def lower_avg(self) -> float:
        return self.__inner._29388_lower_avg()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, H: Optional[int] = None, Alpha: Optional[float] = None, X0: Optional[int] = None, AtrLength: Optional[int] = None, NearFactor: Optional[float] = None, FarFactor: Optional[float] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_a0ed1d(ctx, _30246_input_8c5Jms=H,_30248_input_ryj1d6=Alpha,_30250_input_23yvh7=X0,_30255_input_HQSy15=AtrLength,_30258_input_DtdkCx=NearFactor,_30260_input_iRYo4G=FarFactor)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          