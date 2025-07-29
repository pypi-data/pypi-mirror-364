
  
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

    fastBullishColor: Tuple[int, int, int, int]
    

    normalBullishColor: Tuple[int, int, int, int]
    

    slowBullishColor: Tuple[int, int, int, int]
    

    fastBearishColor: Tuple[int, int, int, int]
    

    normalBearishColor: Tuple[int, int, int, int]
    

    slowBearishColor: Tuple[int, int, int, int]
    

    c_bullish: Tuple[int, int, int, int]
    

    c_bearish: Tuple[int, int, int, int]
    

    bearishCross: List[bool]
    

    bullishCross: List[bool]
    

    slowBearishMedianCross: List[bool]
    

    slowBullishMedianCross: List[bool]
    

    normalBearishMedianCross: List[bool]
    

    normalBullishMedianCross: List[bool]
    

    fastBearishMedianCross: List[bool]
    

    fastBullishMedianCross: List[bool]
    

    yhat0: List[float]
    

    yhat1: List[float]
    

    isBearishKernelTrend: List[bool]
    

    isBullishKernelTrend: List[bool]
    

    isBearishDivZone: List[bool]
    

    isBullishDivZone: List[bool]
    

    isBearishTriggerWave: List[bool]
    

    isBullishTriggerWave: List[bool]
    

    condition: List[int]
    
    pass

class MainResult(TypedDict):
    alerts: List[MainAlert]
    locals: MainResultLocals


def main(ctx: Ctx, Src: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, UseMirror: Optional[bool] = None, UseEma: Optional[bool] = None, EmaLength: Optional[int] = None, UseCog: Optional[bool] = None, CogLength: Optional[int] = None, OscillatorLookback: Optional[int] = None, QuadraticMeanLength: Optional[int] = None, SpeedToEmphasize: Optional[str] = None, EmphasisWidth: Optional[int] = None, UseKernelMa: Optional[bool] = None, UseKernelEmphasis: Optional[bool] = None, Offset: Optional[int] = None, ShowOsc: Optional[bool] = None, FLength: Optional[float] = None, FSmoothing: Optional[float] = None, NLength: Optional[float] = None, NSmoothing: Optional[float] = None, SLength: Optional[float] = None, SSmoothing: Optional[float] = None, DivThreshold: Optional[int] = None, SizePercent: Optional[int] = None, ShowObOs: Optional[bool] = None, InvertObOsColors: Optional[bool] = None, Ob1: Optional[float] = None, Ob2: Optional[float] = None, Os1: Optional[float] = None, Os2: Optional[float] = None, AreaBackgroundTrans: Optional[float] = None, AreaForegroundTrans: Optional[float] = None, LineBackgroundTrans: Optional[float] = None, LineForegroundTrans: Optional[float] = None, CustomTransparency: Optional[int] = None, MaxStepsForGradient: Optional[int] = None, FastBullishColor: Optional[Tuple[int, int, int, int]] = None, NormalBullishColor: Optional[Tuple[int, int, int, int]] = None, SlowBullishColor: Optional[Tuple[int, int, int, int]] = None, FastBearishColor: Optional[Tuple[int, int, int, int]] = None, NormalBearishColor: Optional[Tuple[int, int, int, int]] = None, SlowBearishColor: Optional[Tuple[int, int, int, int]] = None, CBullish: Optional[Tuple[int, int, int, int]] = None, CBearish: Optional[Tuple[int, int, int, int]] = None) -> MainResult:
    """
`main() -> void`
    """
    return _lib.Incr_fn_main_3c85bb(ctx=ctx, _30103_input_IbA9Yl=Src,_30105_input_LzIRIl=UseMirror,_30107_input_7EMmI5=UseEma,_30109_input_T7tfnO=EmaLength,_30111_input_bezkei=UseCog,_30113_input_s4fojR=CogLength,_30115_input_6jBCa8=OscillatorLookback,_30117_input_jXDQU7=QuadraticMeanLength,_30121_input_l2QX1B=SpeedToEmphasize,_30123_input_PO1VcM=EmphasisWidth,_30125_input_QfseXJ=UseKernelMa,_30127_input_sIdOHK=UseKernelEmphasis,_30129_input_rXFvj4=Offset,_30131_input_xPh1fR=ShowOsc,_30133_input_f2Lqdt=FLength,_30135_input_6iJFtH=FSmoothing,_30137_input_MTaxcV=NLength,_30139_input_TTiIBf=NSmoothing,_30141_input_YYAePQ=SLength,_30143_input_dLH9zn=SSmoothing,_30145_input_goBLjQ=DivThreshold,_30147_input_pBrsBd=SizePercent,_30149_input_YSybNL=ShowObOs,_30151_input_IS8qoS=InvertObOsColors,_30153_input_NSdRi1=Ob1,_30155_input_Qtbk85=Ob2,_30157_input_4ISkVv=Os1,_30159_input_C43ryo=Os2,_30161_input_cl2zJE=AreaBackgroundTrans,_30163_input_ZY1Bw4=AreaForegroundTrans,_30165_input_hpKHqj=LineBackgroundTrans,_30167_input_OFpwzM=LineForegroundTrans,_30169_input_7I1EWi=CustomTransparency,_30171_input_nSLgAw=MaxStepsForGradient,_30174_input_uelioR=FastBullishColor,_30177_input_DTje6M=NormalBullishColor,_30180_input_fusOGO=SlowBullishColor,_30183_input_d3UF0u=FastBearishColor,_30186_input_wMpwZw=NormalBearishColor,_30189_input_jMtf9U=SlowBearishColor,_30191_input_RfrtNS=CBullish,_30193_input_BEmXvQ=CBearish).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def fastBullishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._29235_fastBullishColor()
  

    @property
    def normalBullishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._29236_normalBullishColor()
  

    @property
    def slowBullishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._29237_slowBullishColor()
  

    @property
    def fastBearishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._29238_fastBearishColor()
  

    @property
    def normalBearishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._29239_normalBearishColor()
  

    @property
    def slowBearishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._29240_slowBearishColor()
  

    @property
    def c_bullish(self) -> Tuple[int, int, int, int]:
        return self.__inner._29241_c_bullish()
  

    @property
    def c_bearish(self) -> Tuple[int, int, int, int]:
        return self.__inner._29242_c_bearish()
  

    @property
    def bearishCross(self) -> bool:
        return self.__inner._29325_bearishCross()
  

    @property
    def bullishCross(self) -> bool:
        return self.__inner._29326_bullishCross()
  

    @property
    def slowBearishMedianCross(self) -> bool:
        return self.__inner._29327_slowBearishMedianCross()
  

    @property
    def slowBullishMedianCross(self) -> bool:
        return self.__inner._29328_slowBullishMedianCross()
  

    @property
    def normalBearishMedianCross(self) -> bool:
        return self.__inner._29329_normalBearishMedianCross()
  

    @property
    def normalBullishMedianCross(self) -> bool:
        return self.__inner._29330_normalBullishMedianCross()
  

    @property
    def fastBearishMedianCross(self) -> bool:
        return self.__inner._29331_fastBearishMedianCross()
  

    @property
    def fastBullishMedianCross(self) -> bool:
        return self.__inner._29332_fastBullishMedianCross()
  

    @property
    def yhat0(self) -> float:
        return self.__inner._29338_yhat0()
  

    @property
    def yhat1(self) -> float:
        return self.__inner._29339_yhat1()
  

    @property
    def isBearishKernelTrend(self) -> bool:
        return self.__inner._29340_isBearishKernelTrend()
  

    @property
    def isBullishKernelTrend(self) -> bool:
        return self.__inner._29341_isBullishKernelTrend()
  

    @property
    def isBearishDivZone(self) -> bool:
        return self.__inner._29342_isBearishDivZone()
  

    @property
    def isBullishDivZone(self) -> bool:
        return self.__inner._29343_isBullishDivZone()
  

    @property
    def isBearishTriggerWave(self) -> bool:
        return self.__inner._29344_isBearishTriggerWave()
  

    @property
    def isBullishTriggerWave(self) -> bool:
        return self.__inner._29345_isBullishTriggerWave()
  

    @property
    def condition(self) -> int:
        return self.__inner._29346_condition()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, Src: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, UseMirror: Optional[bool] = None, UseEma: Optional[bool] = None, EmaLength: Optional[int] = None, UseCog: Optional[bool] = None, CogLength: Optional[int] = None, OscillatorLookback: Optional[int] = None, QuadraticMeanLength: Optional[int] = None, SpeedToEmphasize: Optional[str] = None, EmphasisWidth: Optional[int] = None, UseKernelMa: Optional[bool] = None, UseKernelEmphasis: Optional[bool] = None, Offset: Optional[int] = None, ShowOsc: Optional[bool] = None, FLength: Optional[float] = None, FSmoothing: Optional[float] = None, NLength: Optional[float] = None, NSmoothing: Optional[float] = None, SLength: Optional[float] = None, SSmoothing: Optional[float] = None, DivThreshold: Optional[int] = None, SizePercent: Optional[int] = None, ShowObOs: Optional[bool] = None, InvertObOsColors: Optional[bool] = None, Ob1: Optional[float] = None, Ob2: Optional[float] = None, Os1: Optional[float] = None, Os2: Optional[float] = None, AreaBackgroundTrans: Optional[float] = None, AreaForegroundTrans: Optional[float] = None, LineBackgroundTrans: Optional[float] = None, LineForegroundTrans: Optional[float] = None, CustomTransparency: Optional[int] = None, MaxStepsForGradient: Optional[int] = None, FastBullishColor: Optional[Tuple[int, int, int, int]] = None, NormalBullishColor: Optional[Tuple[int, int, int, int]] = None, SlowBullishColor: Optional[Tuple[int, int, int, int]] = None, FastBearishColor: Optional[Tuple[int, int, int, int]] = None, NormalBearishColor: Optional[Tuple[int, int, int, int]] = None, SlowBearishColor: Optional[Tuple[int, int, int, int]] = None, CBullish: Optional[Tuple[int, int, int, int]] = None, CBearish: Optional[Tuple[int, int, int, int]] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_3c85bb(ctx, _30103_input_IbA9Yl=Src,_30105_input_LzIRIl=UseMirror,_30107_input_7EMmI5=UseEma,_30109_input_T7tfnO=EmaLength,_30111_input_bezkei=UseCog,_30113_input_s4fojR=CogLength,_30115_input_6jBCa8=OscillatorLookback,_30117_input_jXDQU7=QuadraticMeanLength,_30121_input_l2QX1B=SpeedToEmphasize,_30123_input_PO1VcM=EmphasisWidth,_30125_input_QfseXJ=UseKernelMa,_30127_input_sIdOHK=UseKernelEmphasis,_30129_input_rXFvj4=Offset,_30131_input_xPh1fR=ShowOsc,_30133_input_f2Lqdt=FLength,_30135_input_6iJFtH=FSmoothing,_30137_input_MTaxcV=NLength,_30139_input_TTiIBf=NSmoothing,_30141_input_YYAePQ=SLength,_30143_input_dLH9zn=SSmoothing,_30145_input_goBLjQ=DivThreshold,_30147_input_pBrsBd=SizePercent,_30149_input_YSybNL=ShowObOs,_30151_input_IS8qoS=InvertObOsColors,_30153_input_NSdRi1=Ob1,_30155_input_Qtbk85=Ob2,_30157_input_4ISkVv=Os1,_30159_input_C43ryo=Os2,_30161_input_cl2zJE=AreaBackgroundTrans,_30163_input_ZY1Bw4=AreaForegroundTrans,_30165_input_hpKHqj=LineBackgroundTrans,_30167_input_OFpwzM=LineForegroundTrans,_30169_input_7I1EWi=CustomTransparency,_30171_input_nSLgAw=MaxStepsForGradient,_30174_input_uelioR=FastBullishColor,_30177_input_DTje6M=NormalBullishColor,_30180_input_fusOGO=SlowBullishColor,_30183_input_d3UF0u=FastBearishColor,_30186_input_wMpwZw=NormalBearishColor,_30189_input_jMtf9U=SlowBearishColor,_30191_input_RfrtNS=CBullish,_30193_input_BEmXvQ=CBearish)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          