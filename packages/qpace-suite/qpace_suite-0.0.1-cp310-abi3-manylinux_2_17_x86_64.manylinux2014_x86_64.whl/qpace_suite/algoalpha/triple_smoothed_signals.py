
  
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
    return _lib.Incr_fn_main_c43c62(ctx=ctx, _26719_input_mNS61i=Slength,_26721_input_kEs5Mf=Siglen,_26723_input_h8BOmH=Src,_26725_input_GJW71E=Mat,_26727_input_EhCWZP=Mat1,_26729_input_oe1Z7x=Green,_26731_input_61lr5T=Red).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def v1(self) -> float:
        return self.__inner._25796_v1()
  

    @property
    def v2(self) -> float:
        return self.__inner._25797_v2()
  

    @property
    def dist(self) -> float:
        return self.__inner._25798_dist()
  

    @property
    def ndist(self) -> float:
        return self.__inner._25799_ndist()
  

    @property
    def h(self) -> float:
        return self.__inner._25800_h()
  

    @property
    def l(self) -> float:
        return self.__inner._25801_l()
  

    @property
    def midp(self) -> float:
        return self.__inner._25802_midp()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, Slength: Optional[int] = None, Siglen: Optional[int] = None, Src: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, Mat: Optional[str] = None, Mat1: Optional[str] = None, Green: Optional[Tuple[int, int, int, int]] = None, Red: Optional[Tuple[int, int, int, int]] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_c43c62(ctx, _26719_input_mNS61i=Slength,_26721_input_kEs5Mf=Siglen,_26723_input_h8BOmH=Src,_26725_input_GJW71E=Mat,_26727_input_EhCWZP=Mat1,_26729_input_oe1Z7x=Green,_26731_input_61lr5T=Red)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          