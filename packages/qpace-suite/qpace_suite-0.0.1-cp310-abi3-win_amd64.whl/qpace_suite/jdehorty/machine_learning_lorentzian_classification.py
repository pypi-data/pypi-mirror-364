
  
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
    return _lib.Incr_fn_main_155939(ctx=ctx, _21147_input_AFozHy=generalSettingsSource,_21149_input_A8LWI8=generalSettingsNeighborsCount,_21151_input_QJTAaI=generalSettingsMaxBarsBack,_21153_input_1HG2B0=featureEngineeringFeatureCount,_21155_input_Leo4i7=generalSettingsColorCompression,_21157_input_AyC0Yy=exitsGeneralSettingsShowDefaultExits,_21159_input_0IITEV=exitsGeneralSettingsUseDynamicExits,_21162_input_dgbeKh=ShowTradeStats,_21164_input_wKZ2e4=UseWorstCase,_21166_input_v1g7eR=filtersUseVolatilityFilter,_21168_input_vuGAAq=regimeFiltersUseRegimeFilter,_21170_input_E6Soa9=adxFiltersUseAdxFilter,_21172_input_LXfAIz=regimeFiltersThreshold,_21174_input_8jN09I=adxFiltersThreshold,_21181_input_uRJ9AY=F1String,_21183_input_kDsWIu=F1ParamA,_21185_input_l2hR42=F1ParamB,_21187_input_yVfrgq=F2String,_21189_input_22z73U=F2ParamA,_21191_input_NgjOus=F2ParamB,_21193_input_VatEsJ=F3String,_21195_input_bTBrSg=F3ParamA,_21197_input_i3kk2e=F3ParamB,_21199_input_oxyRID=F4String,_21201_input_fdBpOK=F4ParamA,_21203_input_3lZthc=F4ParamB,_21205_input_pl1dKb=F5String,_21207_input_2tDAA3=F5ParamA,_21209_input_vpOrIE=F5ParamB,_21229_input_jUtBzX=UseEmaFilter,_21231_input_DeWcoM=EmaPeriod,_21235_input_Jg5t6P=UseSmaFilter,_21237_input_mPEpRi=SmaPeriod,_21241_input_AcxiLt=UseKernelFilter,_21243_input_YYVe7q=ShowKernelEstimate,_21245_input_7GJo9V=UseKernelSmoothing,_21247_input_UNXYkT=H,_21249_input_O1U1v9=R,_21251_input_KoN3g6=X,_21253_input_qrEmro=Lag,_21255_input_9XJMFH=ShowBarColors,_21257_input_8Dt7pl=ShowBarPredictions,_21259_input_kPwiF9=UseAtrOffset,_21261_input_oXeTpx=BarPredictionsOffset).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def prediction(self) -> float:
        return self.__inner._20332_prediction()
  

    @property
    def signal(self) -> int:
        return self.__inner._20333_signal()
  

    @property
    def barsHeld(self) -> int:
        return self.__inner._20341_barsHeld()
  

    @property
    def kernelEstimate(self) -> float:
        return self.__inner._20357_kernelEstimate()
  

    @property
    def startLongTrade(self) -> bool:
        return self.__inner._20375_startLongTrade()
  

    @property
    def startShortTrade(self) -> bool:
        return self.__inner._20376_startShortTrade()
  

    @property
    def endLongTrade(self) -> bool:
        return self.__inner._20390_endLongTrade()
  

    @property
    def endShortTrade(self) -> bool:
        return self.__inner._20391_endShortTrade()
  

    @property
    def backTestStream(self) -> int:
        return self.__inner._20399_backTestStream()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, generalSettingsSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, generalSettingsNeighborsCount: Optional[int] = None, generalSettingsMaxBarsBack: Optional[int] = None, featureEngineeringFeatureCount: Optional[int] = None, generalSettingsColorCompression: Optional[int] = None, exitsGeneralSettingsShowDefaultExits: Optional[bool] = None, exitsGeneralSettingsUseDynamicExits: Optional[bool] = None, ShowTradeStats: Optional[bool] = None, UseWorstCase: Optional[bool] = None, filtersUseVolatilityFilter: Optional[bool] = None, regimeFiltersUseRegimeFilter: Optional[bool] = None, adxFiltersUseAdxFilter: Optional[bool] = None, regimeFiltersThreshold: Optional[float] = None, adxFiltersThreshold: Optional[int] = None, F1String: Optional[str] = None, F1ParamA: Optional[int] = None, F1ParamB: Optional[int] = None, F2String: Optional[str] = None, F2ParamA: Optional[int] = None, F2ParamB: Optional[int] = None, F3String: Optional[str] = None, F3ParamA: Optional[int] = None, F3ParamB: Optional[int] = None, F4String: Optional[str] = None, F4ParamA: Optional[int] = None, F4ParamB: Optional[int] = None, F5String: Optional[str] = None, F5ParamA: Optional[int] = None, F5ParamB: Optional[int] = None, UseEmaFilter: Optional[bool] = None, EmaPeriod: Optional[int] = None, UseSmaFilter: Optional[bool] = None, SmaPeriod: Optional[int] = None, UseKernelFilter: Optional[bool] = None, ShowKernelEstimate: Optional[bool] = None, UseKernelSmoothing: Optional[bool] = None, H: Optional[int] = None, R: Optional[float] = None, X: Optional[int] = None, Lag: Optional[int] = None, ShowBarColors: Optional[bool] = None, ShowBarPredictions: Optional[bool] = None, UseAtrOffset: Optional[bool] = None, BarPredictionsOffset: Optional[float] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_155939(ctx, _21147_input_AFozHy=generalSettingsSource,_21149_input_A8LWI8=generalSettingsNeighborsCount,_21151_input_QJTAaI=generalSettingsMaxBarsBack,_21153_input_1HG2B0=featureEngineeringFeatureCount,_21155_input_Leo4i7=generalSettingsColorCompression,_21157_input_AyC0Yy=exitsGeneralSettingsShowDefaultExits,_21159_input_0IITEV=exitsGeneralSettingsUseDynamicExits,_21162_input_dgbeKh=ShowTradeStats,_21164_input_wKZ2e4=UseWorstCase,_21166_input_v1g7eR=filtersUseVolatilityFilter,_21168_input_vuGAAq=regimeFiltersUseRegimeFilter,_21170_input_E6Soa9=adxFiltersUseAdxFilter,_21172_input_LXfAIz=regimeFiltersThreshold,_21174_input_8jN09I=adxFiltersThreshold,_21181_input_uRJ9AY=F1String,_21183_input_kDsWIu=F1ParamA,_21185_input_l2hR42=F1ParamB,_21187_input_yVfrgq=F2String,_21189_input_22z73U=F2ParamA,_21191_input_NgjOus=F2ParamB,_21193_input_VatEsJ=F3String,_21195_input_bTBrSg=F3ParamA,_21197_input_i3kk2e=F3ParamB,_21199_input_oxyRID=F4String,_21201_input_fdBpOK=F4ParamA,_21203_input_3lZthc=F4ParamB,_21205_input_pl1dKb=F5String,_21207_input_2tDAA3=F5ParamA,_21209_input_vpOrIE=F5ParamB,_21229_input_jUtBzX=UseEmaFilter,_21231_input_DeWcoM=EmaPeriod,_21235_input_Jg5t6P=UseSmaFilter,_21237_input_mPEpRi=SmaPeriod,_21241_input_AcxiLt=UseKernelFilter,_21243_input_YYVe7q=ShowKernelEstimate,_21245_input_7GJo9V=UseKernelSmoothing,_21247_input_UNXYkT=H,_21249_input_O1U1v9=R,_21251_input_KoN3g6=X,_21253_input_qrEmro=Lag,_21255_input_9XJMFH=ShowBarColors,_21257_input_8Dt7pl=ShowBarPredictions,_21259_input_kPwiF9=UseAtrOffset,_21261_input_oXeTpx=BarPredictionsOffset)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          