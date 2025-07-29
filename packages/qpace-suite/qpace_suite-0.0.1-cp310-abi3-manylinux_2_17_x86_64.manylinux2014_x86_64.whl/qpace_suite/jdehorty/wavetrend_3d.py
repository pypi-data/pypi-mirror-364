
  
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
    return _lib.Incr_fn_main_cd4e61(ctx=ctx, _27184_input_vMuMjl=Src,_27186_input_LM1AOQ=UseMirror,_27188_input_GA6XNu=UseEma,_27190_input_AFSU20=EmaLength,_27192_input_TX2eLw=UseCog,_27194_input_troA1F=CogLength,_27196_input_2xAeYE=OscillatorLookback,_27198_input_vIRHKb=QuadraticMeanLength,_27202_input_yzEpJk=SpeedToEmphasize,_27204_input_bo2gNn=EmphasisWidth,_27206_input_ZGDcPR=UseKernelMa,_27208_input_6B2OUM=UseKernelEmphasis,_27210_input_SjhtNM=Offset,_27212_input_m87f9O=ShowOsc,_27214_input_wlKBKb=FLength,_27216_input_MCGSxS=FSmoothing,_27218_input_dis58u=NLength,_27220_input_fPFllq=NSmoothing,_27222_input_XyYYPK=SLength,_27224_input_6cguqV=SSmoothing,_27226_input_ch7mHE=DivThreshold,_27228_input_ucdXJT=SizePercent,_27230_input_tXBO7S=ShowObOs,_27232_input_Ucr9ve=InvertObOsColors,_27234_input_d02OJR=Ob1,_27236_input_8uKYxL=Ob2,_27238_input_AkXN7B=Os1,_27240_input_YmGJSW=Os2,_27242_input_dp2e9y=AreaBackgroundTrans,_27244_input_P1z88s=AreaForegroundTrans,_27246_input_8lgNSh=LineBackgroundTrans,_27248_input_6LYQqe=LineForegroundTrans,_27250_input_XwD0hl=CustomTransparency,_27252_input_RqG931=MaxStepsForGradient,_27255_input_chcSPZ=FastBullishColor,_27258_input_QDiQOk=NormalBullishColor,_27261_input_HE30LX=SlowBullishColor,_27264_input_a4QFOj=FastBearishColor,_27267_input_Jp7HF1=NormalBearishColor,_27270_input_MIw0Dt=SlowBearishColor,_27272_input_V5WAnH=CBullish,_27274_input_H4IGD8=CBearish).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def fastBullishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._26316_fastBullishColor()
  

    @property
    def normalBullishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._26317_normalBullishColor()
  

    @property
    def slowBullishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._26318_slowBullishColor()
  

    @property
    def fastBearishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._26319_fastBearishColor()
  

    @property
    def normalBearishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._26320_normalBearishColor()
  

    @property
    def slowBearishColor(self) -> Tuple[int, int, int, int]:
        return self.__inner._26321_slowBearishColor()
  

    @property
    def c_bullish(self) -> Tuple[int, int, int, int]:
        return self.__inner._26322_c_bullish()
  

    @property
    def c_bearish(self) -> Tuple[int, int, int, int]:
        return self.__inner._26323_c_bearish()
  

    @property
    def bearishCross(self) -> bool:
        return self.__inner._26406_bearishCross()
  

    @property
    def bullishCross(self) -> bool:
        return self.__inner._26407_bullishCross()
  

    @property
    def slowBearishMedianCross(self) -> bool:
        return self.__inner._26408_slowBearishMedianCross()
  

    @property
    def slowBullishMedianCross(self) -> bool:
        return self.__inner._26409_slowBullishMedianCross()
  

    @property
    def normalBearishMedianCross(self) -> bool:
        return self.__inner._26410_normalBearishMedianCross()
  

    @property
    def normalBullishMedianCross(self) -> bool:
        return self.__inner._26411_normalBullishMedianCross()
  

    @property
    def fastBearishMedianCross(self) -> bool:
        return self.__inner._26412_fastBearishMedianCross()
  

    @property
    def fastBullishMedianCross(self) -> bool:
        return self.__inner._26413_fastBullishMedianCross()
  

    @property
    def yhat0(self) -> float:
        return self.__inner._26419_yhat0()
  

    @property
    def yhat1(self) -> float:
        return self.__inner._26420_yhat1()
  

    @property
    def isBearishKernelTrend(self) -> bool:
        return self.__inner._26421_isBearishKernelTrend()
  

    @property
    def isBullishKernelTrend(self) -> bool:
        return self.__inner._26422_isBullishKernelTrend()
  

    @property
    def isBearishDivZone(self) -> bool:
        return self.__inner._26423_isBearishDivZone()
  

    @property
    def isBullishDivZone(self) -> bool:
        return self.__inner._26424_isBullishDivZone()
  

    @property
    def isBearishTriggerWave(self) -> bool:
        return self.__inner._26425_isBearishTriggerWave()
  

    @property
    def isBullishTriggerWave(self) -> bool:
        return self.__inner._26426_isBullishTriggerWave()
  

    @property
    def condition(self) -> int:
        return self.__inner._26427_condition()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, Src: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, UseMirror: Optional[bool] = None, UseEma: Optional[bool] = None, EmaLength: Optional[int] = None, UseCog: Optional[bool] = None, CogLength: Optional[int] = None, OscillatorLookback: Optional[int] = None, QuadraticMeanLength: Optional[int] = None, SpeedToEmphasize: Optional[str] = None, EmphasisWidth: Optional[int] = None, UseKernelMa: Optional[bool] = None, UseKernelEmphasis: Optional[bool] = None, Offset: Optional[int] = None, ShowOsc: Optional[bool] = None, FLength: Optional[float] = None, FSmoothing: Optional[float] = None, NLength: Optional[float] = None, NSmoothing: Optional[float] = None, SLength: Optional[float] = None, SSmoothing: Optional[float] = None, DivThreshold: Optional[int] = None, SizePercent: Optional[int] = None, ShowObOs: Optional[bool] = None, InvertObOsColors: Optional[bool] = None, Ob1: Optional[float] = None, Ob2: Optional[float] = None, Os1: Optional[float] = None, Os2: Optional[float] = None, AreaBackgroundTrans: Optional[float] = None, AreaForegroundTrans: Optional[float] = None, LineBackgroundTrans: Optional[float] = None, LineForegroundTrans: Optional[float] = None, CustomTransparency: Optional[int] = None, MaxStepsForGradient: Optional[int] = None, FastBullishColor: Optional[Tuple[int, int, int, int]] = None, NormalBullishColor: Optional[Tuple[int, int, int, int]] = None, SlowBullishColor: Optional[Tuple[int, int, int, int]] = None, FastBearishColor: Optional[Tuple[int, int, int, int]] = None, NormalBearishColor: Optional[Tuple[int, int, int, int]] = None, SlowBearishColor: Optional[Tuple[int, int, int, int]] = None, CBullish: Optional[Tuple[int, int, int, int]] = None, CBearish: Optional[Tuple[int, int, int, int]] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_cd4e61(ctx, _27184_input_vMuMjl=Src,_27186_input_LM1AOQ=UseMirror,_27188_input_GA6XNu=UseEma,_27190_input_AFSU20=EmaLength,_27192_input_TX2eLw=UseCog,_27194_input_troA1F=CogLength,_27196_input_2xAeYE=OscillatorLookback,_27198_input_vIRHKb=QuadraticMeanLength,_27202_input_yzEpJk=SpeedToEmphasize,_27204_input_bo2gNn=EmphasisWidth,_27206_input_ZGDcPR=UseKernelMa,_27208_input_6B2OUM=UseKernelEmphasis,_27210_input_SjhtNM=Offset,_27212_input_m87f9O=ShowOsc,_27214_input_wlKBKb=FLength,_27216_input_MCGSxS=FSmoothing,_27218_input_dis58u=NLength,_27220_input_fPFllq=NSmoothing,_27222_input_XyYYPK=SLength,_27224_input_6cguqV=SSmoothing,_27226_input_ch7mHE=DivThreshold,_27228_input_ucdXJT=SizePercent,_27230_input_tXBO7S=ShowObOs,_27232_input_Ucr9ve=InvertObOsColors,_27234_input_d02OJR=Ob1,_27236_input_8uKYxL=Ob2,_27238_input_AkXN7B=Os1,_27240_input_YmGJSW=Os2,_27242_input_dp2e9y=AreaBackgroundTrans,_27244_input_P1z88s=AreaForegroundTrans,_27246_input_8lgNSh=LineBackgroundTrans,_27248_input_6LYQqe=LineForegroundTrans,_27250_input_XwD0hl=CustomTransparency,_27252_input_RqG931=MaxStepsForGradient,_27255_input_chcSPZ=FastBullishColor,_27258_input_QDiQOk=NormalBullishColor,_27261_input_HE30LX=SlowBullishColor,_27264_input_a4QFOj=FastBearishColor,_27267_input_Jp7HF1=NormalBearishColor,_27270_input_MIw0Dt=SlowBearishColor,_27272_input_V5WAnH=CBullish,_27274_input_H4IGD8=CBearish)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          