
  
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

    v1: List[float]
    

    v2: List[float]
    

    dist: List[float]
    

    ndist: List[float]
    

    h: List[float]
    

    l: List[float]
    

    midp: List[float]
    
    pass

class MainResult(TypedDict):
    alerts: List[MainAlert]
    locals: MainResultLocals


def main(ctx: Ctx, Slength: Optional[int] = None, Siglen: Optional[int] = None, Src: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, Mat: Optional[str] = None, Mat1: Optional[str] = None, Green: Optional[Tuple[int, int, int, int]] = None, Red: Optional[Tuple[int, int, int, int]] = None) -> MainResult:
    """
`main() -> void`
    """
    return _lib.Incr_fn_main_cff98a(ctx=ctx, _32557_input_40y2NY=Slength,_32559_input_5Xszzn=Siglen,_32561_input_OeWfKy=Src,_32563_input_v52VJS=Mat,_32565_input_iKo5tC=Mat1,_32567_input_pR51Em=Green,_32569_input_2c8A8m=Red).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def v1(self) -> float:
        return self.__inner._31634_v1()
  

    @property
    def v2(self) -> float:
        return self.__inner._31635_v2()
  

    @property
    def dist(self) -> float:
        return self.__inner._31636_dist()
  

    @property
    def ndist(self) -> float:
        return self.__inner._31637_ndist()
  

    @property
    def h(self) -> float:
        return self.__inner._31638_h()
  

    @property
    def l(self) -> float:
        return self.__inner._31639_l()
  

    @property
    def midp(self) -> float:
        return self.__inner._31640_midp()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, Slength: Optional[int] = None, Siglen: Optional[int] = None, Src: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, Mat: Optional[str] = None, Mat1: Optional[str] = None, Green: Optional[Tuple[int, int, int, int]] = None, Red: Optional[Tuple[int, int, int, int]] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_cff98a(ctx, _32557_input_40y2NY=Slength,_32559_input_5Xszzn=Siglen,_32561_input_OeWfKy=Src,_32563_input_v52VJS=Mat,_32565_input_iKo5tC=Mat1,_32567_input_pR51Em=Green,_32569_input_2c8A8m=Red)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          