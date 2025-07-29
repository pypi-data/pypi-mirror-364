
  
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
    return _lib.Incr_fn_main_0d7f4f(ctx=ctx, _32488_input_OEYWuJ=Length,_32490_input_jcrDbK=Mult).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def fbasis(self) -> float:
        return self.__inner._31545_fbasis()
  

    @property
    def rangge(self) -> float:
        return self.__inner._31546_rangge()
  

    @property
    def dev(self) -> float:
        return self.__inner._31547_dev()
  

    @property
    def vol(self) -> float:
        return self.__inner._31548_vol()
  

    @property
    def upper(self) -> float:
        return self.__inner._31549_upper()
  

    @property
    def lower(self) -> float:
        return self.__inner._31550_lower()
  

    @property
    def fu(self) -> float:
        return self.__inner._31551_fu()
  

    @property
    def fl(self) -> float:
        return self.__inner._31552_fl()
  

    @property
    def uu(self) -> float:
        return self.__inner._31553_uu()
  

    @property
    def ul(self) -> float:
        return self.__inner._31554_ul()
  

    @property
    def lu(self) -> float:
        return self.__inner._31555_lu()
  

    @property
    def ll(self) -> float:
        return self.__inner._31556_ll()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, Length: Optional[int] = None, Mult: Optional[float] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_0d7f4f(ctx, _32488_input_OEYWuJ=Length,_32490_input_jcrDbK=Mult)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          