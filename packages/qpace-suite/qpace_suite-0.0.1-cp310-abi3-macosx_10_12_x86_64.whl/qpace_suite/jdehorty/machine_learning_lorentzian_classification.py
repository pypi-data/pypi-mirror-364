
  
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
    return _lib.Incr_fn_main_49a414(ctx=ctx, _24066_input_Hd6w3x=generalSettingsSource,_24068_input_m9Y5rq=generalSettingsNeighborsCount,_24070_input_wesT9I=generalSettingsMaxBarsBack,_24072_input_xzTgzK=featureEngineeringFeatureCount,_24074_input_qcCl0i=generalSettingsColorCompression,_24076_input_2crX9h=exitsGeneralSettingsShowDefaultExits,_24078_input_stiQ2v=exitsGeneralSettingsUseDynamicExits,_24081_input_ZzP6Yv=ShowTradeStats,_24083_input_NvQH85=UseWorstCase,_24085_input_GaCAGp=filtersUseVolatilityFilter,_24087_input_IhHudS=regimeFiltersUseRegimeFilter,_24089_input_DaBhL9=adxFiltersUseAdxFilter,_24091_input_l7NmYq=regimeFiltersThreshold,_24093_input_HetPBD=adxFiltersThreshold,_24100_input_0MG3Lv=F1String,_24102_input_NAKgiu=F1ParamA,_24104_input_9o1HY6=F1ParamB,_24106_input_FWocjb=F2String,_24108_input_u8a7oU=F2ParamA,_24110_input_a3vyiL=F2ParamB,_24112_input_43S4SM=F3String,_24114_input_jQPb5b=F3ParamA,_24116_input_oKoG9L=F3ParamB,_24118_input_88KbmF=F4String,_24120_input_7gWHUt=F4ParamA,_24122_input_6MAdDv=F4ParamB,_24124_input_HRQHbE=F5String,_24126_input_PDp1v8=F5ParamA,_24128_input_5E2dAT=F5ParamB,_24148_input_2gCLEe=UseEmaFilter,_24150_input_wptJfq=EmaPeriod,_24154_input_X9eeiE=UseSmaFilter,_24156_input_hzdJC1=SmaPeriod,_24160_input_YugH5F=UseKernelFilter,_24162_input_GsmFBJ=ShowKernelEstimate,_24164_input_uRFwVt=UseKernelSmoothing,_24166_input_yWmm2e=H,_24168_input_eiiCTv=R,_24170_input_N0mRsi=X,_24172_input_20rrDN=Lag,_24174_input_UvgPUA=ShowBarColors,_24176_input_aRn0lf=ShowBarPredictions,_24178_input_w93Q8P=UseAtrOffset,_24180_input_n1f0ji=BarPredictionsOffset).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def prediction(self) -> float:
        return self.__inner._23251_prediction()
  

    @property
    def signal(self) -> int:
        return self.__inner._23252_signal()
  

    @property
    def barsHeld(self) -> int:
        return self.__inner._23260_barsHeld()
  

    @property
    def kernelEstimate(self) -> float:
        return self.__inner._23276_kernelEstimate()
  

    @property
    def startLongTrade(self) -> bool:
        return self.__inner._23294_startLongTrade()
  

    @property
    def startShortTrade(self) -> bool:
        return self.__inner._23295_startShortTrade()
  

    @property
    def endLongTrade(self) -> bool:
        return self.__inner._23309_endLongTrade()
  

    @property
    def endShortTrade(self) -> bool:
        return self.__inner._23310_endShortTrade()
  

    @property
    def backTestStream(self) -> int:
        return self.__inner._23318_backTestStream()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, generalSettingsSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, generalSettingsNeighborsCount: Optional[int] = None, generalSettingsMaxBarsBack: Optional[int] = None, featureEngineeringFeatureCount: Optional[int] = None, generalSettingsColorCompression: Optional[int] = None, exitsGeneralSettingsShowDefaultExits: Optional[bool] = None, exitsGeneralSettingsUseDynamicExits: Optional[bool] = None, ShowTradeStats: Optional[bool] = None, UseWorstCase: Optional[bool] = None, filtersUseVolatilityFilter: Optional[bool] = None, regimeFiltersUseRegimeFilter: Optional[bool] = None, adxFiltersUseAdxFilter: Optional[bool] = None, regimeFiltersThreshold: Optional[float] = None, adxFiltersThreshold: Optional[int] = None, F1String: Optional[str] = None, F1ParamA: Optional[int] = None, F1ParamB: Optional[int] = None, F2String: Optional[str] = None, F2ParamA: Optional[int] = None, F2ParamB: Optional[int] = None, F3String: Optional[str] = None, F3ParamA: Optional[int] = None, F3ParamB: Optional[int] = None, F4String: Optional[str] = None, F4ParamA: Optional[int] = None, F4ParamB: Optional[int] = None, F5String: Optional[str] = None, F5ParamA: Optional[int] = None, F5ParamB: Optional[int] = None, UseEmaFilter: Optional[bool] = None, EmaPeriod: Optional[int] = None, UseSmaFilter: Optional[bool] = None, SmaPeriod: Optional[int] = None, UseKernelFilter: Optional[bool] = None, ShowKernelEstimate: Optional[bool] = None, UseKernelSmoothing: Optional[bool] = None, H: Optional[int] = None, R: Optional[float] = None, X: Optional[int] = None, Lag: Optional[int] = None, ShowBarColors: Optional[bool] = None, ShowBarPredictions: Optional[bool] = None, UseAtrOffset: Optional[bool] = None, BarPredictionsOffset: Optional[float] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_49a414(ctx, _24066_input_Hd6w3x=generalSettingsSource,_24068_input_m9Y5rq=generalSettingsNeighborsCount,_24070_input_wesT9I=generalSettingsMaxBarsBack,_24072_input_xzTgzK=featureEngineeringFeatureCount,_24074_input_qcCl0i=generalSettingsColorCompression,_24076_input_2crX9h=exitsGeneralSettingsShowDefaultExits,_24078_input_stiQ2v=exitsGeneralSettingsUseDynamicExits,_24081_input_ZzP6Yv=ShowTradeStats,_24083_input_NvQH85=UseWorstCase,_24085_input_GaCAGp=filtersUseVolatilityFilter,_24087_input_IhHudS=regimeFiltersUseRegimeFilter,_24089_input_DaBhL9=adxFiltersUseAdxFilter,_24091_input_l7NmYq=regimeFiltersThreshold,_24093_input_HetPBD=adxFiltersThreshold,_24100_input_0MG3Lv=F1String,_24102_input_NAKgiu=F1ParamA,_24104_input_9o1HY6=F1ParamB,_24106_input_FWocjb=F2String,_24108_input_u8a7oU=F2ParamA,_24110_input_a3vyiL=F2ParamB,_24112_input_43S4SM=F3String,_24114_input_jQPb5b=F3ParamA,_24116_input_oKoG9L=F3ParamB,_24118_input_88KbmF=F4String,_24120_input_7gWHUt=F4ParamA,_24122_input_6MAdDv=F4ParamB,_24124_input_HRQHbE=F5String,_24126_input_PDp1v8=F5ParamA,_24128_input_5E2dAT=F5ParamB,_24148_input_2gCLEe=UseEmaFilter,_24150_input_wptJfq=EmaPeriod,_24154_input_X9eeiE=UseSmaFilter,_24156_input_hzdJC1=SmaPeriod,_24160_input_YugH5F=UseKernelFilter,_24162_input_GsmFBJ=ShowKernelEstimate,_24164_input_uRFwVt=UseKernelSmoothing,_24166_input_yWmm2e=H,_24168_input_eiiCTv=R,_24170_input_N0mRsi=X,_24172_input_20rrDN=Lag,_24174_input_UvgPUA=ShowBarColors,_24176_input_aRn0lf=ShowBarPredictions,_24178_input_w93Q8P=UseAtrOffset,_24180_input_n1f0ji=BarPredictionsOffset)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          