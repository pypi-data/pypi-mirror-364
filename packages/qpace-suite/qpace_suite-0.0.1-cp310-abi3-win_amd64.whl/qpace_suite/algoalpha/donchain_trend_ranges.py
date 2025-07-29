
  
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

    fbasis: List[float]
    

    rangge: List[float]
    

    dev: List[float]
    

    vol: List[float]
    

    upper: List[float]
    

    lower: List[float]
    

    fu: List[float]
    

    fl: List[float]
    

    uu: List[float]
    

    ul: List[float]
    

    lu: List[float]
    

    ll: List[float]
    
    pass

class MainResult(TypedDict):
    alerts: List[MainAlert]
    locals: MainResultLocals


def main(ctx: Ctx, Length: Optional[int] = None, Mult: Optional[float] = None) -> MainResult:
    """
`main() -> void`
    """
    return _lib.Incr_fn_main_655781(ctx=ctx, _20812_input_gaITgZ=Length,_20814_input_xevtpJ=Mult).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def fbasis(self) -> float:
        return self.__inner._19869_fbasis()
  

    @property
    def rangge(self) -> float:
        return self.__inner._19870_rangge()
  

    @property
    def dev(self) -> float:
        return self.__inner._19871_dev()
  

    @property
    def vol(self) -> float:
        return self.__inner._19872_vol()
  

    @property
    def upper(self) -> float:
        return self.__inner._19873_upper()
  

    @property
    def lower(self) -> float:
        return self.__inner._19874_lower()
  

    @property
    def fu(self) -> float:
        return self.__inner._19875_fu()
  

    @property
    def fl(self) -> float:
        return self.__inner._19876_fl()
  

    @property
    def uu(self) -> float:
        return self.__inner._19877_uu()
  

    @property
    def ul(self) -> float:
        return self.__inner._19878_ul()
  

    @property
    def lu(self) -> float:
        return self.__inner._19879_lu()
  

    @property
    def ll(self) -> float:
        return self.__inner._19880_ll()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, Length: Optional[int] = None, Mult: Optional[float] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_655781(ctx, _20812_input_gaITgZ=Length,_20814_input_xevtpJ=Mult)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          