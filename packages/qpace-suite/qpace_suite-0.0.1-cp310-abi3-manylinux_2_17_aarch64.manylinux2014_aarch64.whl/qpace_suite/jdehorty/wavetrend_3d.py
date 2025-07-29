
  
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
    return _lib.Incr_fn_main_63d6e0(ctx=ctx, _33022_input_5gycgy=Src,_33024_input_o2JiGk=UseMirror,_33026_input_muA1Tz=UseEma,_33028_input_norfme=EmaLength,_33030_input_wCMglb=UseCog,_33032_input_1I8IFq=CogLength,_33034_input_qol7gz=OscillatorLookback,_33036_input_XTSNBY=QuadraticMeanLength,_33040_input_SoJyhr=SpeedToEmphasize,_33042_input_zXVli2=EmphasisWidth,_33044_input_DwjJUZ=UseKernelMa,_33046_input_bY5Uzi=UseKernelEmphasis,_33048_input_N2CJYe=Offset,_33050_input_SA2TAp=ShowOsc,_33052_input_jXYQsZ=FLength,_33054_input_fpmKRD=FSmoothing,_33056_input_3AMR1C=NLength,_33058_input_XEt81U=NSmoothing,_33060_input_57ii9b=SLength,_33062_input_CjcIbJ=SSmoothing,_33064_input_I0LaYZ=DivThreshold,_33066_input_Cvak0G=SizePercent,_33068_input_gycFNB=ShowObOs,_33070_input_XGo6Pf=InvertObOsColors,_33072_input_i7Ktrp=Ob1,_33074_input_mBkkJq=Ob2,_33076_input_KZTaRx=Os1,_33078_input_E2JTxp=Os2,_33080_input_tzeENz=AreaBackgroundTrans,_33082_input_mYIvvd=AreaForegroundTrans,_33084_input_uOV7pE=LineBackgroundTrans,_33086_input_m6n0Pw=LineForegroundTrans,_33088_input_98Dp4e=CustomTransparency,_33090_input_SLxUlT=MaxStepsForGradient,_33093_input_dLy1Zm=FastBullishColor,_33096_input_byAPne=NormalBullishColor,_33099_input_Yuotsz=SlowBullishColor,_33102_input_mKvkst=FastBearishColor,_33105_input_yppz5K=NormalBearishColor,_33108_input_4yLM39=SlowBearishColor,_33110_input_Y02kug=CBullish,_33112_input_YS1u4l=CBearish).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def fastBullishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._32154_fastBullishColor()
  

    @property
    def normalBullishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._32155_normalBullishColor()
  

    @property
    def slowBullishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._32156_slowBullishColor()
  

    @property
    def fastBearishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._32157_fastBearishColor()
  

    @property
    def normalBearishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._32158_normalBearishColor()
  

    @property
    def slowBearishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._32159_slowBearishColor()
  

    @property
    def c_bullish(self) -> Tuple[int, int, int, int]:
        return self.__inner._32160_c_bullish()
  

    @property
    def c_bearish(self) -> Tuple[int, int, int, int]:
        return self.__inner._32161_c_bearish()
  

    @property
    def bearishCross(self) -> bool:
        return self.__inner._32244_bearishCross()
  

    @property
    def bullishCross(self) -> bool:
        return self.__inner._32245_bullishCross()
  

    @property
    def slowBearishMedianCross(self) -> bool:
        return self.__inner._32246_slowBearishMedianCross()
  

    @property
    def slowBullishMedianCross(self) -> bool:
        return self.__inner._32247_slowBullishMedianCross()
  

    @property
    def normalBearishMedianCross(self) -> bool:
        return self.__inner._32248_normalBearishMedianCross()
  

    @property
    def normalBullishMedianCross(self) -> bool:
        return self.__inner._32249_normalBullishMedianCross()
  

    @property
    def fastBearishMedianCross(self) -> bool:
        return self.__inner._32250_fastBearishMedianCross()
  

    @property
    def fastBullishMedianCross(self) -> bool:
        return self.__inner._32251_fastBullishMedianCross()
  

    @property
    def yhat0(self) -> float:
        return self.__inner._32257_yhat0()
  

    @property
    def yhat1(self) -> float:
        return self.__inner._32258_yhat1()
  

    @property
    def isBearishKernelTrend(self) -> bool:
        return self.__inner._32259_isBearishKernelTrend()
  

    @property
    def isBullishKernelTrend(self) -> bool:
        return self.__inner._32260_isBullishKernelTrend()
  

    @property
    def isBearishDivZone(self) -> bool:
        return self.__inner._32261_isBearishDivZone()
  

    @property
    def isBullishDivZone(self) -> bool:
        return self.__inner._32262_isBullishDivZone()
  

    @property
    def isBearishTriggerWave(self) -> bool:
        return self.__inner._32263_isBearishTriggerWave()
  

    @property
    def isBullishTriggerWave(self) -> bool:
        return self.__inner._32264_isBullishTriggerWave()
  

    @property
    def condition(self) -> int:
        return self.__inner._32265_condition()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, Src: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, UseMirror: Optional[bool] = None, UseEma: Optional[bool] = None, EmaLength: Optional[int] = None, UseCog: Optional[bool] = None, CogLength: Optional[int] = None, OscillatorLookback: Optional[int] = None, QuadraticMeanLength: Optional[int] = None, SpeedToEmphasize: Optional[str] = None, EmphasisWidth: Optional[int] = None, UseKernelMa: Optional[bool] = None, UseKernelEmphasis: Optional[bool] = None, Offset: Optional[int] = None, ShowOsc: Optional[bool] = None, FLength: Optional[float] = None, FSmoothing: Optional[float] = None, NLength: Optional[float] = None, NSmoothing: Optional[float] = None, SLength: Optional[float] = None, SSmoothing: Optional[float] = None, DivThreshold: Optional[int] = None, SizePercent: Optional[int] = None, ShowObOs: Optional[bool] = None, InvertObOsColors: Optional[bool] = None, Ob1: Optional[float] = None, Ob2: Optional[float] = None, Os1: Optional[float] = None, Os2: Optional[float] = None, AreaBackgroundTrans: Optional[float] = None, AreaForegroundTrans: Optional[float] = None, LineBackgroundTrans: Optional[float] = None, LineForegroundTrans: Optional[float] = None, CustomTransparency: Optional[int] = None, MaxStepsForGradient: Optional[int] = None, FastBullishColor: Optional[Tuple[int, int, int, int]] = None, NormalBullishColor: Optional[Tuple[int, int, int, int]] = None, SlowBullishColor: Optional[Tuple[int, int, int, int]] = None, FastBearishColor: Optional[Tuple[int, int, int, int]] = None, NormalBearishColor: Optional[Tuple[int, int, int, int]] = None, SlowBearishColor: Optional[Tuple[int, int, int, int]] = None, CBullish: Optional[Tuple[int, int, int, int]] = None, CBearish: Optional[Tuple[int, int, int, int]] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_63d6e0(ctx, _33022_input_5gycgy=Src,_33024_input_o2JiGk=UseMirror,_33026_input_muA1Tz=UseEma,_33028_input_norfme=EmaLength,_33030_input_wCMglb=UseCog,_33032_input_1I8IFq=CogLength,_33034_input_qol7gz=OscillatorLookback,_33036_input_XTSNBY=QuadraticMeanLength,_33040_input_SoJyhr=SpeedToEmphasize,_33042_input_zXVli2=EmphasisWidth,_33044_input_DwjJUZ=UseKernelMa,_33046_input_bY5Uzi=UseKernelEmphasis,_33048_input_N2CJYe=Offset,_33050_input_SA2TAp=ShowOsc,_33052_input_jXYQsZ=FLength,_33054_input_fpmKRD=FSmoothing,_33056_input_3AMR1C=NLength,_33058_input_XEt81U=NSmoothing,_33060_input_57ii9b=SLength,_33062_input_CjcIbJ=SSmoothing,_33064_input_I0LaYZ=DivThreshold,_33066_input_Cvak0G=SizePercent,_33068_input_gycFNB=ShowObOs,_33070_input_XGo6Pf=InvertObOsColors,_33072_input_i7Ktrp=Ob1,_33074_input_mBkkJq=Ob2,_33076_input_KZTaRx=Os1,_33078_input_E2JTxp=Os2,_33080_input_tzeENz=AreaBackgroundTrans,_33082_input_mYIvvd=AreaForegroundTrans,_33084_input_uOV7pE=LineBackgroundTrans,_33086_input_m6n0Pw=LineForegroundTrans,_33088_input_98Dp4e=CustomTransparency,_33090_input_SLxUlT=MaxStepsForGradient,_33093_input_dLy1Zm=FastBullishColor,_33096_input_byAPne=NormalBullishColor,_33099_input_Yuotsz=SlowBullishColor,_33102_input_mKvkst=FastBearishColor,_33105_input_yppz5K=NormalBearishColor,_33108_input_4yLM39=SlowBearishColor,_33110_input_Y02kug=CBullish,_33112_input_YS1u4l=CBearish)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          