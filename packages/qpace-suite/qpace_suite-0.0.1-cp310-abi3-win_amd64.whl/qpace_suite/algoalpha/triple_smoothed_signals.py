
  
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
    return _lib.Incr_fn_main_e7c922(ctx=ctx, _20881_input_PvkqD3=Slength,_20883_input_EQPP1q=Siglen,_20885_input_3d0XVn=Src,_20887_input_53CQ3S=Mat,_20889_input_69wuvM=Mat1,_20891_input_TDPTrf=Green,_20893_input_PqGAT1=Red).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def v1(self) -> float:
        return self.__inner._19958_v1()
  

    @property
    def v2(self) -> float:
        return self.__inner._19959_v2()
  

    @property
    def dist(self) -> float:
        return self.__inner._19960_dist()
  

    @property
    def ndist(self) -> float:
        return self.__inner._19961_ndist()
  

    @property
    def h(self) -> float:
        return self.__inner._19962_h()
  

    @property
    def l(self) -> float:
        return self.__inner._19963_l()
  

    @property
    def midp(self) -> float:
        return self.__inner._19964_midp()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, Slength: Optional[int] = None, Siglen: Optional[int] = None, Src: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, Mat: Optional[str] = None, Mat1: Optional[str] = None, Green: Optional[Tuple[int, int, int, int]] = None, Red: Optional[Tuple[int, int, int, int]] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_e7c922(ctx, _20881_input_PvkqD3=Slength,_20883_input_EQPP1q=Siglen,_20885_input_3d0XVn=Src,_20887_input_53CQ3S=Mat,_20889_input_69wuvM=Mat1,_20891_input_TDPTrf=Green,_20893_input_PqGAT1=Red)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          