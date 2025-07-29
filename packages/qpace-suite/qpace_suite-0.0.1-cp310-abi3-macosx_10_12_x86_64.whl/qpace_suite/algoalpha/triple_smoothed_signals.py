
  
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
    return _lib.Incr_fn_main_be8a4a(ctx=ctx, _23800_input_AvlkSq=Slength,_23802_input_1ykuUq=Siglen,_23804_input_XmZWXS=Src,_23806_input_cKiuCf=Mat,_23808_input_QNlmTl=Mat1,_23810_input_7PRTRP=Green,_23812_input_oBfsXX=Red).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def v1(self) -> float:
        return self.__inner._22877_v1()
  

    @property
    def v2(self) -> float:
        return self.__inner._22878_v2()
  

    @property
    def dist(self) -> float:
        return self.__inner._22879_dist()
  

    @property
    def ndist(self) -> float:
        return self.__inner._22880_ndist()
  

    @property
    def h(self) -> float:
        return self.__inner._22881_h()
  

    @property
    def l(self) -> float:
        return self.__inner._22882_l()
  

    @property
    def midp(self) -> float:
        return self.__inner._22883_midp()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, Slength: Optional[int] = None, Siglen: Optional[int] = None, Src: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, Mat: Optional[str] = None, Mat1: Optional[str] = None, Green: Optional[Tuple[int, int, int, int]] = None, Red: Optional[Tuple[int, int, int, int]] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_be8a4a(ctx, _23800_input_AvlkSq=Slength,_23802_input_1ykuUq=Siglen,_23804_input_XmZWXS=Src,_23806_input_cKiuCf=Mat,_23808_input_QNlmTl=Mat1,_23810_input_7PRTRP=Green,_23812_input_oBfsXX=Red)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          