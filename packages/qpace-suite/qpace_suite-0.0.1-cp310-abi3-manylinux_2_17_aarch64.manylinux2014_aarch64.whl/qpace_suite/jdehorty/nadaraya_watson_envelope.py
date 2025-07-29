
  
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
    return _lib.Incr_fn_main_127b0f(ctx=ctx, _33165_input_xuh57m=H,_33167_input_9Vihvc=Alpha,_33169_input_VgPb0k=X0,_33174_input_q4xhN3=AtrLength,_33177_input_q84K9g=NearFactor,_33179_input_nqjkuW=FarFactor).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def yhat_close(self) -> float:
        return self.__inner._32288_yhat_close()
  

    @property
    def yhat_high(self) -> float:
        return self.__inner._32289_yhat_high()
  

    @property
    def yhat_low(self) -> float:
        return self.__inner._32290_yhat_low()
  

    @property
    def yhat(self) -> float:
        return self.__inner._32291_yhat()
  

    @property
    def ktr(self) -> float:
        return self.__inner._32292_ktr()
  

    @property
    def upper_near(self) -> float:
        return self.__inner._32302_upper_near()
  

    @property
    def upper_far(self) -> float:
        return self.__inner._32303_upper_far()
  

    @property
    def upper_avg(self) -> float:
        return self.__inner._32304_upper_avg()
  

    @property
    def lower_near(self) -> float:
        return self.__inner._32305_lower_near()
  

    @property
    def lower_far(self) -> float:
        return self.__inner._32306_lower_far()
  

    @property
    def lower_avg(self) -> float:
        return self.__inner._32307_lower_avg()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, H: Optional[int] = None, Alpha: Optional[float] = None, X0: Optional[int] = None, AtrLength: Optional[int] = None, NearFactor: Optional[float] = None, FarFactor: Optional[float] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_127b0f(ctx, _33165_input_xuh57m=H,_33167_input_9Vihvc=Alpha,_33169_input_VgPb0k=X0,_33174_input_q4xhN3=AtrLength,_33177_input_q84K9g=NearFactor,_33179_input_nqjkuW=FarFactor)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          