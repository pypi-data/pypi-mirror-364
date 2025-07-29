
  
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
    return _lib.Incr_fn_main_87d9fe(ctx=ctx, _24265_input_t1bNo3=Src,_24267_input_d5jjnG=UseMirror,_24269_input_Jb07JY=UseEma,_24271_input_z9UZb2=EmaLength,_24273_input_NuyByH=UseCog,_24275_input_yfUoHM=CogLength,_24277_input_L1UC6D=OscillatorLookback,_24279_input_4GAeaG=QuadraticMeanLength,_24283_input_7crQKQ=SpeedToEmphasize,_24285_input_dE9tOm=EmphasisWidth,_24287_input_OW6fAO=UseKernelMa,_24289_input_PvYgho=UseKernelEmphasis,_24291_input_nYZJxK=Offset,_24293_input_iIGvHB=ShowOsc,_24295_input_0KMYpf=FLength,_24297_input_V0H4aG=FSmoothing,_24299_input_zdL9gH=NLength,_24301_input_pLEOEN=NSmoothing,_24303_input_bkqTZx=SLength,_24305_input_y3XXgs=SSmoothing,_24307_input_Rp3wVY=DivThreshold,_24309_input_mcSoZ7=SizePercent,_24311_input_i68big=ShowObOs,_24313_input_pVpigK=InvertObOsColors,_24315_input_p1BAAv=Ob1,_24317_input_OQKC0n=Ob2,_24319_input_bwGxl6=Os1,_24321_input_fp24xZ=Os2,_24323_input_AVZSPb=AreaBackgroundTrans,_24325_input_jrlowd=AreaForegroundTrans,_24327_input_L1cQKa=LineBackgroundTrans,_24329_input_udEoVk=LineForegroundTrans,_24331_input_VHB8WW=CustomTransparency,_24333_input_kxzMb7=MaxStepsForGradient,_24336_input_y23dKD=FastBullishColor,_24339_input_Bs9DkF=NormalBullishColor,_24342_input_KGngP7=SlowBullishColor,_24345_input_oi5Fl3=FastBearishColor,_24348_input_cLnj9l=NormalBearishColor,_24351_input_x1HFLz=SlowBearishColor,_24353_input_gPlgbJ=CBullish,_24355_input_JRoWAp=CBearish).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def fastBullishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._23397_fastBullishColor()
  

    @property
    def normalBullishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._23398_normalBullishColor()
  

    @property
    def slowBullishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._23399_slowBullishColor()
  

    @property
    def fastBearishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._23400_fastBearishColor()
  

    @property
    def normalBearishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._23401_normalBearishColor()
  

    @property
    def slowBearishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._23402_slowBearishColor()
  

    @property
    def c_bullish(self) -> Tuple[int, int, int, int]:
        return self.__inner._23403_c_bullish()
  

    @property
    def c_bearish(self) -> Tuple[int, int, int, int]:
        return self.__inner._23404_c_bearish()
  

    @property
    def bearishCross(self) -> bool:
        return self.__inner._23487_bearishCross()
  

    @property
    def bullishCross(self) -> bool:
        return self.__inner._23488_bullishCross()
  

    @property
    def slowBearishMedianCross(self) -> bool:
        return self.__inner._23489_slowBearishMedianCross()
  

    @property
    def slowBullishMedianCross(self) -> bool:
        return self.__inner._23490_slowBullishMedianCross()
  

    @property
    def normalBearishMedianCross(self) -> bool:
        return self.__inner._23491_normalBearishMedianCross()
  

    @property
    def normalBullishMedianCross(self) -> bool:
        return self.__inner._23492_normalBullishMedianCross()
  

    @property
    def fastBearishMedianCross(self) -> bool:
        return self.__inner._23493_fastBearishMedianCross()
  

    @property
    def fastBullishMedianCross(self) -> bool:
        return self.__inner._23494_fastBullishMedianCross()
  

    @property
    def yhat0(self) -> float:
        return self.__inner._23500_yhat0()
  

    @property
    def yhat1(self) -> float:
        return self.__inner._23501_yhat1()
  

    @property
    def isBearishKernelTrend(self) -> bool:
        return self.__inner._23502_isBearishKernelTrend()
  

    @property
    def isBullishKernelTrend(self) -> bool:
        return self.__inner._23503_isBullishKernelTrend()
  

    @property
    def isBearishDivZone(self) -> bool:
        return self.__inner._23504_isBearishDivZone()
  

    @property
    def isBullishDivZone(self) -> bool:
        return self.__inner._23505_isBullishDivZone()
  

    @property
    def isBearishTriggerWave(self) -> bool:
        return self.__inner._23506_isBearishTriggerWave()
  

    @property
    def isBullishTriggerWave(self) -> bool:
        return self.__inner._23507_isBullishTriggerWave()
  

    @property
    def condition(self) -> int:
        return self.__inner._23508_condition()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, Src: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, UseMirror: Optional[bool] = None, UseEma: Optional[bool] = None, EmaLength: Optional[int] = None, UseCog: Optional[bool] = None, CogLength: Optional[int] = None, OscillatorLookback: Optional[int] = None, QuadraticMeanLength: Optional[int] = None, SpeedToEmphasize: Optional[str] = None, EmphasisWidth: Optional[int] = None, UseKernelMa: Optional[bool] = None, UseKernelEmphasis: Optional[bool] = None, Offset: Optional[int] = None, ShowOsc: Optional[bool] = None, FLength: Optional[float] = None, FSmoothing: Optional[float] = None, NLength: Optional[float] = None, NSmoothing: Optional[float] = None, SLength: Optional[float] = None, SSmoothing: Optional[float] = None, DivThreshold: Optional[int] = None, SizePercent: Optional[int] = None, ShowObOs: Optional[bool] = None, InvertObOsColors: Optional[bool] = None, Ob1: Optional[float] = None, Ob2: Optional[float] = None, Os1: Optional[float] = None, Os2: Optional[float] = None, AreaBackgroundTrans: Optional[float] = None, AreaForegroundTrans: Optional[float] = None, LineBackgroundTrans: Optional[float] = None, LineForegroundTrans: Optional[float] = None, CustomTransparency: Optional[int] = None, MaxStepsForGradient: Optional[int] = None, FastBullishColor: Optional[Tuple[int, int, int, int]] = None, NormalBullishColor: Optional[Tuple[int, int, int, int]] = None, SlowBullishColor: Optional[Tuple[int, int, int, int]] = None, FastBearishColor: Optional[Tuple[int, int, int, int]] = None, NormalBearishColor: Optional[Tuple[int, int, int, int]] = None, SlowBearishColor: Optional[Tuple[int, int, int, int]] = None, CBullish: Optional[Tuple[int, int, int, int]] = None, CBearish: Optional[Tuple[int, int, int, int]] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_87d9fe(ctx, _24265_input_t1bNo3=Src,_24267_input_d5jjnG=UseMirror,_24269_input_Jb07JY=UseEma,_24271_input_z9UZb2=EmaLength,_24273_input_NuyByH=UseCog,_24275_input_yfUoHM=CogLength,_24277_input_L1UC6D=OscillatorLookback,_24279_input_4GAeaG=QuadraticMeanLength,_24283_input_7crQKQ=SpeedToEmphasize,_24285_input_dE9tOm=EmphasisWidth,_24287_input_OW6fAO=UseKernelMa,_24289_input_PvYgho=UseKernelEmphasis,_24291_input_nYZJxK=Offset,_24293_input_iIGvHB=ShowOsc,_24295_input_0KMYpf=FLength,_24297_input_V0H4aG=FSmoothing,_24299_input_zdL9gH=NLength,_24301_input_pLEOEN=NSmoothing,_24303_input_bkqTZx=SLength,_24305_input_y3XXgs=SSmoothing,_24307_input_Rp3wVY=DivThreshold,_24309_input_mcSoZ7=SizePercent,_24311_input_i68big=ShowObOs,_24313_input_pVpigK=InvertObOsColors,_24315_input_p1BAAv=Ob1,_24317_input_OQKC0n=Ob2,_24319_input_bwGxl6=Os1,_24321_input_fp24xZ=Os2,_24323_input_AVZSPb=AreaBackgroundTrans,_24325_input_jrlowd=AreaForegroundTrans,_24327_input_L1cQKa=LineBackgroundTrans,_24329_input_udEoVk=LineForegroundTrans,_24331_input_VHB8WW=CustomTransparency,_24333_input_kxzMb7=MaxStepsForGradient,_24336_input_y23dKD=FastBullishColor,_24339_input_Bs9DkF=NormalBullishColor,_24342_input_KGngP7=SlowBullishColor,_24345_input_oi5Fl3=FastBearishColor,_24348_input_cLnj9l=NormalBearishColor,_24351_input_x1HFLz=SlowBearishColor,_24353_input_gPlgbJ=CBullish,_24355_input_JRoWAp=CBearish)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          