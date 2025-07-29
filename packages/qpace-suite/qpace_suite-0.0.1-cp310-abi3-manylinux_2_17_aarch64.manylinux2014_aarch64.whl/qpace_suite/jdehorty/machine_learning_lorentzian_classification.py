
  
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

    prediction: List[float]
    

    signal: List[int]
    

    barsHeld: List[int]
    

    kernelEstimate: List[float]
    

    startLongTrade: List[bool]
    

    startShortTrade: List[bool]
    

    endLongTrade: List[bool]
    

    endShortTrade: List[bool]
    

    backTestStream: List[int]
    
    pass

class MainResult(TypedDict):
    alerts: List[MainAlert]
    locals: MainResultLocals


def main(ctx: Ctx, generalSettingsSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, generalSettingsNeighborsCount: Optional[int] = None, generalSettingsMaxBarsBack: Optional[int] = None, featureEngineeringFeatureCount: Optional[int] = None, generalSettingsColorCompression: Optional[int] = None, exitsGeneralSettingsShowDefaultExits: Optional[bool] = None, exitsGeneralSettingsUseDynamicExits: Optional[bool] = None, ShowTradeStats: Optional[bool] = None, UseWorstCase: Optional[bool] = None, filtersUseVolatilityFilter: Optional[bool] = None, regimeFiltersUseRegimeFilter: Optional[bool] = None, adxFiltersUseAdxFilter: Optional[bool] = None, regimeFiltersThreshold: Optional[float] = None, adxFiltersThreshold: Optional[int] = None, F1String: Optional[str] = None, F1ParamA: Optional[int] = None, F1ParamB: Optional[int] = None, F2String: Optional[str] = None, F2ParamA: Optional[int] = None, F2ParamB: Optional[int] = None, F3String: Optional[str] = None, F3ParamA: Optional[int] = None, F3ParamB: Optional[int] = None, F4String: Optional[str] = None, F4ParamA: Optional[int] = None, F4ParamB: Optional[int] = None, F5String: Optional[str] = None, F5ParamA: Optional[int] = None, F5ParamB: Optional[int] = None, UseEmaFilter: Optional[bool] = None, EmaPeriod: Optional[int] = None, UseSmaFilter: Optional[bool] = None, SmaPeriod: Optional[int] = None, UseKernelFilter: Optional[bool] = None, ShowKernelEstimate: Optional[bool] = None, UseKernelSmoothing: Optional[bool] = None, H: Optional[int] = None, R: Optional[float] = None, X: Optional[int] = None, Lag: Optional[int] = None, ShowBarColors: Optional[bool] = None, ShowBarPredictions: Optional[bool] = None, UseAtrOffset: Optional[bool] = None, BarPredictionsOffset: Optional[float] = None) -> MainResult:
    """
`main() -> void`
    """
    return _lib.Incr_fn_main_50aa71(ctx=ctx, _32823_input_9tamTW=generalSettingsSource,_32825_input_2bWLnJ=generalSettingsNeighborsCount,_32827_input_uo2oCM=generalSettingsMaxBarsBack,_32829_input_ohRGR8=featureEngineeringFeatureCount,_32831_input_FVOZHR=generalSettingsColorCompression,_32833_input_aYLTE6=exitsGeneralSettingsShowDefaultExits,_32835_input_CFrLVU=exitsGeneralSettingsUseDynamicExits,_32838_input_yERIzI=ShowTradeStats,_32840_input_X0iK0n=UseWorstCase,_32842_input_mPQXsd=filtersUseVolatilityFilter,_32844_input_I9ikyW=regimeFiltersUseRegimeFilter,_32846_input_pugADq=adxFiltersUseAdxFilter,_32848_input_gcLGDW=regimeFiltersThreshold,_32850_input_MKjh25=adxFiltersThreshold,_32857_input_nOBi2e=F1String,_32859_input_KIvKg3=F1ParamA,_32861_input_8sts0o=F1ParamB,_32863_input_YOQLsK=F2String,_32865_input_szdSJn=F2ParamA,_32867_input_9BGbOz=F2ParamB,_32869_input_mcjiOu=F3String,_32871_input_3LFpjD=F3ParamA,_32873_input_7RCZGU=F3ParamB,_32875_input_Rj87pW=F4String,_32877_input_B9wD1M=F4ParamA,_32879_input_XfpvkX=F4ParamB,_32881_input_sngzDp=F5String,_32883_input_T5w2DE=F5ParamA,_32885_input_Eb76or=F5ParamB,_32905_input_ypqy88=UseEmaFilter,_32907_input_zP5Jo0=EmaPeriod,_32911_input_qXl4dB=UseSmaFilter,_32913_input_8Etx2S=SmaPeriod,_32917_input_5WWvKB=UseKernelFilter,_32919_input_LpuVG3=ShowKernelEstimate,_32921_input_WSiy0N=UseKernelSmoothing,_32923_input_ryIfv8=H,_32925_input_o15Q1J=R,_32927_input_9fkbQs=X,_32929_input_XWCseK=Lag,_32931_input_EeqwC5=ShowBarColors,_32933_input_MQhCon=ShowBarPredictions,_32935_input_aZn8oy=UseAtrOffset,_32937_input_Bq4Mas=BarPredictionsOffset).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def prediction(self) -> float:
        return self.__inner._32008_prediction()
  

    @property
    def signal(self) -> int:
        return self.__inner._32009_signal()
  

    @property
    def barsHeld(self) -> int:
        return self.__inner._32017_barsHeld()
  

    @property
    def kernelEstimate(self) -> float:
        return self.__inner._32033_kernelEstimate()
  

    @property
    def startLongTrade(self) -> bool:
        return self.__inner._32051_startLongTrade()
  

    @property
    def startShortTrade(self) -> bool:
        return self.__inner._32052_startShortTrade()
  

    @property
    def endLongTrade(self) -> bool:
        return self.__inner._32066_endLongTrade()
  

    @property
    def endShortTrade(self) -> bool:
        return self.__inner._32067_endShortTrade()
  

    @property
    def backTestStream(self) -> int:
        return self.__inner._32075_backTestStream()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, generalSettingsSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, generalSettingsNeighborsCount: Optional[int] = None, generalSettingsMaxBarsBack: Optional[int] = None, featureEngineeringFeatureCount: Optional[int] = None, generalSettingsColorCompression: Optional[int] = None, exitsGeneralSettingsShowDefaultExits: Optional[bool] = None, exitsGeneralSettingsUseDynamicExits: Optional[bool] = None, ShowTradeStats: Optional[bool] = None, UseWorstCase: Optional[bool] = None, filtersUseVolatilityFilter: Optional[bool] = None, regimeFiltersUseRegimeFilter: Optional[bool] = None, adxFiltersUseAdxFilter: Optional[bool] = None, regimeFiltersThreshold: Optional[float] = None, adxFiltersThreshold: Optional[int] = None, F1String: Optional[str] = None, F1ParamA: Optional[int] = None, F1ParamB: Optional[int] = None, F2String: Optional[str] = None, F2ParamA: Optional[int] = None, F2ParamB: Optional[int] = None, F3String: Optional[str] = None, F3ParamA: Optional[int] = None, F3ParamB: Optional[int] = None, F4String: Optional[str] = None, F4ParamA: Optional[int] = None, F4ParamB: Optional[int] = None, F5String: Optional[str] = None, F5ParamA: Optional[int] = None, F5ParamB: Optional[int] = None, UseEmaFilter: Optional[bool] = None, EmaPeriod: Optional[int] = None, UseSmaFilter: Optional[bool] = None, SmaPeriod: Optional[int] = None, UseKernelFilter: Optional[bool] = None, ShowKernelEstimate: Optional[bool] = None, UseKernelSmoothing: Optional[bool] = None, H: Optional[int] = None, R: Optional[float] = None, X: Optional[int] = None, Lag: Optional[int] = None, ShowBarColors: Optional[bool] = None, ShowBarPredictions: Optional[bool] = None, UseAtrOffset: Optional[bool] = None, BarPredictionsOffset: Optional[float] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_50aa71(ctx, _32823_input_9tamTW=generalSettingsSource,_32825_input_2bWLnJ=generalSettingsNeighborsCount,_32827_input_uo2oCM=generalSettingsMaxBarsBack,_32829_input_ohRGR8=featureEngineeringFeatureCount,_32831_input_FVOZHR=generalSettingsColorCompression,_32833_input_aYLTE6=exitsGeneralSettingsShowDefaultExits,_32835_input_CFrLVU=exitsGeneralSettingsUseDynamicExits,_32838_input_yERIzI=ShowTradeStats,_32840_input_X0iK0n=UseWorstCase,_32842_input_mPQXsd=filtersUseVolatilityFilter,_32844_input_I9ikyW=regimeFiltersUseRegimeFilter,_32846_input_pugADq=adxFiltersUseAdxFilter,_32848_input_gcLGDW=regimeFiltersThreshold,_32850_input_MKjh25=adxFiltersThreshold,_32857_input_nOBi2e=F1String,_32859_input_KIvKg3=F1ParamA,_32861_input_8sts0o=F1ParamB,_32863_input_YOQLsK=F2String,_32865_input_szdSJn=F2ParamA,_32867_input_9BGbOz=F2ParamB,_32869_input_mcjiOu=F3String,_32871_input_3LFpjD=F3ParamA,_32873_input_7RCZGU=F3ParamB,_32875_input_Rj87pW=F4String,_32877_input_B9wD1M=F4ParamA,_32879_input_XfpvkX=F4ParamB,_32881_input_sngzDp=F5String,_32883_input_T5w2DE=F5ParamA,_32885_input_Eb76or=F5ParamB,_32905_input_ypqy88=UseEmaFilter,_32907_input_zP5Jo0=EmaPeriod,_32911_input_qXl4dB=UseSmaFilter,_32913_input_8Etx2S=SmaPeriod,_32917_input_5WWvKB=UseKernelFilter,_32919_input_LpuVG3=ShowKernelEstimate,_32921_input_WSiy0N=UseKernelSmoothing,_32923_input_ryIfv8=H,_32925_input_o15Q1J=R,_32927_input_9fkbQs=X,_32929_input_XWCseK=Lag,_32931_input_EeqwC5=ShowBarColors,_32933_input_MQhCon=ShowBarPredictions,_32935_input_aZn8oy=UseAtrOffset,_32937_input_Bq4Mas=BarPredictionsOffset)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          