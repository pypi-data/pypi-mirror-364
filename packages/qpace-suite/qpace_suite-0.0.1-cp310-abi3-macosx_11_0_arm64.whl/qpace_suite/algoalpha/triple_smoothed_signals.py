
  
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
    return _lib.Incr_fn_main_dcd606(ctx=ctx, _29638_input_8fkhZu=Slength,_29640_input_1bdsuV=Siglen,_29642_input_vDSI8p=Src,_29644_input_aauEmY=Mat,_29646_input_SC76Fn=Mat1,_29648_input_97LBOb=Green,_29650_input_bc5qkv=Red).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def v1(self) -> float:
        return self.__inner._28715_v1()
  

    @property
    def v2(self) -> float:
        return self.__inner._28716_v2()
  

    @property
    def dist(self) -> float:
        return self.__inner._28717_dist()
  

    @property
    def ndist(self) -> float:
        return self.__inner._28718_ndist()
  

    @property
    def h(self) -> float:
        return self.__inner._28719_h()
  

    @property
    def l(self) -> float:
        return self.__inner._28720_l()
  

    @property
    def midp(self) -> float:
        return self.__inner._28721_midp()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, Slength: Optional[int] = None, Siglen: Optional[int] = None, Src: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, Mat: Optional[str] = None, Mat1: Optional[str] = None, Green: Optional[Tuple[int, int, int, int]] = None, Red: Optional[Tuple[int, int, int, int]] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_dcd606(ctx, _29638_input_8fkhZu=Slength,_29640_input_1bdsuV=Siglen,_29642_input_vDSI8p=Src,_29644_input_aauEmY=Mat,_29646_input_SC76Fn=Mat1,_29648_input_97LBOb=Green,_29650_input_bc5qkv=Red)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          