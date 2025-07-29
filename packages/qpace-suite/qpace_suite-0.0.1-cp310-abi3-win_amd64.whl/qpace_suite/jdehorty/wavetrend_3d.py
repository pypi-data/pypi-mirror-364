
  
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
    return _lib.Incr_fn_main_2979aa(ctx=ctx, _21346_input_4V4iay=Src,_21348_input_br8O4s=UseMirror,_21350_input_0YQ6fv=UseEma,_21352_input_ALA2Up=EmaLength,_21354_input_afjbvq=UseCog,_21356_input_VsmUsk=CogLength,_21358_input_eS5FWf=OscillatorLookback,_21360_input_C7R3zi=QuadraticMeanLength,_21364_input_9hdt1r=SpeedToEmphasize,_21366_input_CdxGU6=EmphasisWidth,_21368_input_4e2E1s=UseKernelMa,_21370_input_OG1s6X=UseKernelEmphasis,_21372_input_ZW0kBy=Offset,_21374_input_CwEZnO=ShowOsc,_21376_input_rXsQ6z=FLength,_21378_input_dUIXKY=FSmoothing,_21380_input_HY3dgx=NLength,_21382_input_1yYlJl=NSmoothing,_21384_input_IW63aC=SLength,_21386_input_F1i70O=SSmoothing,_21388_input_OHj5gt=DivThreshold,_21390_input_P8U7gm=SizePercent,_21392_input_vzagcF=ShowObOs,_21394_input_XGk2oh=InvertObOsColors,_21396_input_ImIb3z=Ob1,_21398_input_r7mOEc=Ob2,_21400_input_3Fa8GC=Os1,_21402_input_NaShIh=Os2,_21404_input_KUrE9x=AreaBackgroundTrans,_21406_input_tT6m7d=AreaForegroundTrans,_21408_input_xSBwlp=LineBackgroundTrans,_21410_input_cUpHUG=LineForegroundTrans,_21412_input_mNt8oa=CustomTransparency,_21414_input_AdMDdC=MaxStepsForGradient,_21417_input_jwXrhN=FastBullishColor,_21420_input_sNZ9Cq=NormalBullishColor,_21423_input_KpZ1a4=SlowBullishColor,_21426_input_3zoO56=FastBearishColor,_21429_input_hMylQg=NormalBearishColor,_21432_input_w1JOAH=SlowBearishColor,_21434_input_xWxP9x=CBullish,_21436_input_xLtyqD=CBearish).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def fastBullishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._20478_fastBullishColor()
  

    @property
    def normalBullishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._20479_normalBullishColor()
  

    @property
    def slowBullishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._20480_slowBullishColor()
  

    @property
    def fastBearishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._20481_fastBearishColor()
  

    @property
    def normalBearishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._20482_normalBearishColor()
  

    @property
    def slowBearishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._20483_slowBearishColor()
  

    @property
    def c_bullish(self) -> Tuple[int, int, int, int]:
        return self.__inner._20484_c_bullish()
  

    @property
    def c_bearish(self) -> Tuple[int, int, int, int]:
        return self.__inner._20485_c_bearish()
  

    @property
    def bearishCross(self) -> bool:
        return self.__inner._20568_bearishCross()
  

    @property
    def bullishCross(self) -> bool:
        return self.__inner._20569_bullishCross()
  

    @property
    def slowBearishMedianCross(self) -> bool:
        return self.__inner._20570_slowBearishMedianCross()
  

    @property
    def slowBullishMedianCross(self) -> bool:
        return self.__inner._20571_slowBullishMedianCross()
  

    @property
    def normalBearishMedianCross(self) -> bool:
        return self.__inner._20572_normalBearishMedianCross()
  

    @property
    def normalBullishMedianCross(self) -> bool:
        return self.__inner._20573_normalBullishMedianCross()
  

    @property
    def fastBearishMedianCross(self) -> bool:
        return self.__inner._20574_fastBearishMedianCross()
  

    @property
    def fastBullishMedianCross(self) -> bool:
        return self.__inner._20575_fastBullishMedianCross()
  

    @property
    def yhat0(self) -> float:
        return self.__inner._20581_yhat0()
  

    @property
    def yhat1(self) -> float:
        return self.__inner._20582_yhat1()
  

    @property
    def isBearishKernelTrend(self) -> bool:
        return self.__inner._20583_isBearishKernelTrend()
  

    @property
    def isBullishKernelTrend(self) -> bool:
        return self.__inner._20584_isBullishKernelTrend()
  

    @property
    def isBearishDivZone(self) -> bool:
        return self.__inner._20585_isBearishDivZone()
  

    @property
    def isBullishDivZone(self) -> bool:
        return self.__inner._20586_isBullishDivZone()
  

    @property
    def isBearishTriggerWave(self) -> bool:
        return self.__inner._20587_isBearishTriggerWave()
  

    @property
    def isBullishTriggerWave(self) -> bool:
        return self.__inner._20588_isBullishTriggerWave()
  

    @property
    def condition(self) -> int:
        return self.__inner._20589_condition()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, Src: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, UseMirror: Optional[bool] = None, UseEma: Optional[bool] = None, EmaLength: Optional[int] = None, UseCog: Optional[bool] = None, CogLength: Optional[int] = None, OscillatorLookback: Optional[int] = None, QuadraticMeanLength: Optional[int] = None, SpeedToEmphasize: Optional[str] = None, EmphasisWidth: Optional[int] = None, UseKernelMa: Optional[bool] = None, UseKernelEmphasis: Optional[bool] = None, Offset: Optional[int] = None, ShowOsc: Optional[bool] = None, FLength: Optional[float] = None, FSmoothing: Optional[float] = None, NLength: Optional[float] = None, NSmoothing: Optional[float] = None, SLength: Optional[float] = None, SSmoothing: Optional[float] = None, DivThreshold: Optional[int] = None, SizePercent: Optional[int] = None, ShowObOs: Optional[bool] = None, InvertObOsColors: Optional[bool] = None, Ob1: Optional[float] = None, Ob2: Optional[float] = None, Os1: Optional[float] = None, Os2: Optional[float] = None, AreaBackgroundTrans: Optional[float] = None, AreaForegroundTrans: Optional[float] = None, LineBackgroundTrans: Optional[float] = None, LineForegroundTrans: Optional[float] = None, CustomTransparency: Optional[int] = None, MaxStepsForGradient: Optional[int] = None, FastBullishColor: Optional[Tuple[int, int, int, int]] = None, NormalBullishColor: Optional[Tuple[int, int, int, int]] = None, SlowBullishColor: Optional[Tuple[int, int, int, int]] = None, FastBearishColor: Optional[Tuple[int, int, int, int]] = None, NormalBearishColor: Optional[Tuple[int, int, int, int]] = None, SlowBearishColor: Optional[Tuple[int, int, int, int]] = None, CBullish: Optional[Tuple[int, int, int, int]] = None, CBearish: Optional[Tuple[int, int, int, int]] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_2979aa(ctx, _21346_input_4V4iay=Src,_21348_input_br8O4s=UseMirror,_21350_input_0YQ6fv=UseEma,_21352_input_ALA2Up=EmaLength,_21354_input_afjbvq=UseCog,_21356_input_VsmUsk=CogLength,_21358_input_eS5FWf=OscillatorLookback,_21360_input_C7R3zi=QuadraticMeanLength,_21364_input_9hdt1r=SpeedToEmphasize,_21366_input_CdxGU6=EmphasisWidth,_21368_input_4e2E1s=UseKernelMa,_21370_input_OG1s6X=UseKernelEmphasis,_21372_input_ZW0kBy=Offset,_21374_input_CwEZnO=ShowOsc,_21376_input_rXsQ6z=FLength,_21378_input_dUIXKY=FSmoothing,_21380_input_HY3dgx=NLength,_21382_input_1yYlJl=NSmoothing,_21384_input_IW63aC=SLength,_21386_input_F1i70O=SSmoothing,_21388_input_OHj5gt=DivThreshold,_21390_input_P8U7gm=SizePercent,_21392_input_vzagcF=ShowObOs,_21394_input_XGk2oh=InvertObOsColors,_21396_input_ImIb3z=Ob1,_21398_input_r7mOEc=Ob2,_21400_input_3Fa8GC=Os1,_21402_input_NaShIh=Os2,_21404_input_KUrE9x=AreaBackgroundTrans,_21406_input_tT6m7d=AreaForegroundTrans,_21408_input_xSBwlp=LineBackgroundTrans,_21410_input_cUpHUG=LineForegroundTrans,_21412_input_mNt8oa=CustomTransparency,_21414_input_AdMDdC=MaxStepsForGradient,_21417_input_jwXrhN=FastBullishColor,_21420_input_sNZ9Cq=NormalBullishColor,_21423_input_KpZ1a4=SlowBullishColor,_21426_input_3zoO56=FastBearishColor,_21429_input_hMylQg=NormalBearishColor,_21432_input_w1JOAH=SlowBearishColor,_21434_input_xWxP9x=CBullish,_21436_input_xLtyqD=CBearish)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          