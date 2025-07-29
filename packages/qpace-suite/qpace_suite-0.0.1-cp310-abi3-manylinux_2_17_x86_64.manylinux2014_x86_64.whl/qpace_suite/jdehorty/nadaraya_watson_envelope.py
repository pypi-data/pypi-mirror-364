
  
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
    return _lib.Incr_fn_main_a187ef(ctx=ctx, _27327_input_umHtGl=H,_27329_input_RYL3W8=Alpha,_27331_input_Add0h7=X0,_27336_input_sVvTNu=AtrLength,_27339_input_RSfZoY=NearFactor,_27341_input_sPfvDq=FarFactor).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def yhat_close(self) -> float:
        return self.__inner._26450_yhat_close()
  

    @property
    def yhat_high(self) -> float:
        return self.__inner._26451_yhat_high()
  

    @property
    def yhat_low(self) -> float:
        return self.__inner._26452_yhat_low()
  

    @property
    def yhat(self) -> float:
        return self.__inner._26453_yhat()
  

    @property
    def ktr(self) -> float:
        return self.__inner._26454_ktr()
  

    @property
    def upper_near(self) -> float:
        return self.__inner._26464_upper_near()
  

    @property
    def upper_far(self) -> float:
        return self.__inner._26465_upper_far()
  

    @property
    def upper_avg(self) -> float:
        return self.__inner._26466_upper_avg()
  

    @property
    def lower_near(self) -> float:
        return self.__inner._26467_lower_near()
  

    @property
    def lower_far(self) -> float:
        return self.__inner._26468_lower_far()
  

    @property
    def lower_avg(self) -> float:
        return self.__inner._26469_lower_avg()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, H: Optional[int] = None, Alpha: Optional[float] = None, X0: Optional[int] = None, AtrLength: Optional[int] = None, NearFactor: Optional[float] = None, FarFactor: Optional[float] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_a187ef(ctx, _27327_input_umHtGl=H,_27329_input_RYL3W8=Alpha,_27331_input_Add0h7=X0,_27336_input_sVvTNu=AtrLength,_27339_input_RSfZoY=NearFactor,_27341_input_sPfvDq=FarFactor)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          