
  
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
    return _lib.Incr_fn_main_57c9f8(ctx=ctx, _26985_input_pnzT03=generalSettingsSource,_26987_input_9dqh0a=generalSettingsNeighborsCount,_26989_input_G8VqUb=generalSettingsMaxBarsBack,_26991_input_42Oi6V=featureEngineeringFeatureCount,_26993_input_6vfVB6=generalSettingsColorCompression,_26995_input_c1ipXD=exitsGeneralSettingsShowDefaultExits,_26997_input_08tG6f=exitsGeneralSettingsUseDynamicExits,_27000_input_9hFAE8=ShowTradeStats,_27002_input_M0Ckdh=UseWorstCase,_27004_input_hxmwbx=filtersUseVolatilityFilter,_27006_input_oWLtiM=regimeFiltersUseRegimeFilter,_27008_input_kDp5nB=adxFiltersUseAdxFilter,_27010_input_bItx3p=regimeFiltersThreshold,_27012_input_MXe4qa=adxFiltersThreshold,_27019_input_iayMZl=F1String,_27021_input_RHILDu=F1ParamA,_27023_input_4odx00=F1ParamB,_27025_input_tqs6Gs=F2String,_27027_input_apzNdf=F2ParamA,_27029_input_vK0T5j=F2ParamB,_27031_input_r9LUZH=F3String,_27033_input_YaQqf5=F3ParamA,_27035_input_FkyyE9=F3ParamB,_27037_input_n0wcJX=F4String,_27039_input_I1F9mN=F4ParamA,_27041_input_SDkwzV=F4ParamB,_27043_input_7etJ9j=F5String,_27045_input_Txt3mi=F5ParamA,_27047_input_Uw6Lkb=F5ParamB,_27067_input_aJsXVH=UseEmaFilter,_27069_input_BCe986=EmaPeriod,_27073_input_kWlrEj=UseSmaFilter,_27075_input_GTYgX8=SmaPeriod,_27079_input_ICXCYd=UseKernelFilter,_27081_input_WPEynx=ShowKernelEstimate,_27083_input_EHEK7Z=UseKernelSmoothing,_27085_input_ShunaH=H,_27087_input_BUCF0O=R,_27089_input_RtWYuy=X,_27091_input_Ms5fP1=Lag,_27093_input_YP5eOC=ShowBarColors,_27095_input_Toa0vH=ShowBarPredictions,_27097_input_JYZo0F=UseAtrOffset,_27099_input_4lXnaA=BarPredictionsOffset).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def prediction(self) -> float:
        return self.__inner._26170_prediction()
  

    @property
    def signal(self) -> int:
        return self.__inner._26171_signal()
  

    @property
    def barsHeld(self) -> int:
        return self.__inner._26179_barsHeld()
  

    @property
    def kernelEstimate(self) -> float:
        return self.__inner._26195_kernelEstimate()
  

    @property
    def startLongTrade(self) -> bool:
        return self.__inner._26213_startLongTrade()
  

    @property
    def startShortTrade(self) -> bool:
        return self.__inner._26214_startShortTrade()
  

    @property
    def endLongTrade(self) -> bool:
        return self.__inner._26228_endLongTrade()
  

    @property
    def endShortTrade(self) -> bool:
        return self.__inner._26229_endShortTrade()
  

    @property
    def backTestStream(self) -> int:
        return self.__inner._26237_backTestStream()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, generalSettingsSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, generalSettingsNeighborsCount: Optional[int] = None, generalSettingsMaxBarsBack: Optional[int] = None, featureEngineeringFeatureCount: Optional[int] = None, generalSettingsColorCompression: Optional[int] = None, exitsGeneralSettingsShowDefaultExits: Optional[bool] = None, exitsGeneralSettingsUseDynamicExits: Optional[bool] = None, ShowTradeStats: Optional[bool] = None, UseWorstCase: Optional[bool] = None, filtersUseVolatilityFilter: Optional[bool] = None, regimeFiltersUseRegimeFilter: Optional[bool] = None, adxFiltersUseAdxFilter: Optional[bool] = None, regimeFiltersThreshold: Optional[float] = None, adxFiltersThreshold: Optional[int] = None, F1String: Optional[str] = None, F1ParamA: Optional[int] = None, F1ParamB: Optional[int] = None, F2String: Optional[str] = None, F2ParamA: Optional[int] = None, F2ParamB: Optional[int] = None, F3String: Optional[str] = None, F3ParamA: Optional[int] = None, F3ParamB: Optional[int] = None, F4String: Optional[str] = None, F4ParamA: Optional[int] = None, F4ParamB: Optional[int] = None, F5String: Optional[str] = None, F5ParamA: Optional[int] = None, F5ParamB: Optional[int] = None, UseEmaFilter: Optional[bool] = None, EmaPeriod: Optional[int] = None, UseSmaFilter: Optional[bool] = None, SmaPeriod: Optional[int] = None, UseKernelFilter: Optional[bool] = None, ShowKernelEstimate: Optional[bool] = None, UseKernelSmoothing: Optional[bool] = None, H: Optional[int] = None, R: Optional[float] = None, X: Optional[int] = None, Lag: Optional[int] = None, ShowBarColors: Optional[bool] = None, ShowBarPredictions: Optional[bool] = None, UseAtrOffset: Optional[bool] = None, BarPredictionsOffset: Optional[float] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_57c9f8(ctx, _26985_input_pnzT03=generalSettingsSource,_26987_input_9dqh0a=generalSettingsNeighborsCount,_26989_input_G8VqUb=generalSettingsMaxBarsBack,_26991_input_42Oi6V=featureEngineeringFeatureCount,_26993_input_6vfVB6=generalSettingsColorCompression,_26995_input_c1ipXD=exitsGeneralSettingsShowDefaultExits,_26997_input_08tG6f=exitsGeneralSettingsUseDynamicExits,_27000_input_9hFAE8=ShowTradeStats,_27002_input_M0Ckdh=UseWorstCase,_27004_input_hxmwbx=filtersUseVolatilityFilter,_27006_input_oWLtiM=regimeFiltersUseRegimeFilter,_27008_input_kDp5nB=adxFiltersUseAdxFilter,_27010_input_bItx3p=regimeFiltersThreshold,_27012_input_MXe4qa=adxFiltersThreshold,_27019_input_iayMZl=F1String,_27021_input_RHILDu=F1ParamA,_27023_input_4odx00=F1ParamB,_27025_input_tqs6Gs=F2String,_27027_input_apzNdf=F2ParamA,_27029_input_vK0T5j=F2ParamB,_27031_input_r9LUZH=F3String,_27033_input_YaQqf5=F3ParamA,_27035_input_FkyyE9=F3ParamB,_27037_input_n0wcJX=F4String,_27039_input_I1F9mN=F4ParamA,_27041_input_SDkwzV=F4ParamB,_27043_input_7etJ9j=F5String,_27045_input_Txt3mi=F5ParamA,_27047_input_Uw6Lkb=F5ParamB,_27067_input_aJsXVH=UseEmaFilter,_27069_input_BCe986=EmaPeriod,_27073_input_kWlrEj=UseSmaFilter,_27075_input_GTYgX8=SmaPeriod,_27079_input_ICXCYd=UseKernelFilter,_27081_input_WPEynx=ShowKernelEstimate,_27083_input_EHEK7Z=UseKernelSmoothing,_27085_input_ShunaH=H,_27087_input_BUCF0O=R,_27089_input_RtWYuy=X,_27091_input_Ms5fP1=Lag,_27093_input_YP5eOC=ShowBarColors,_27095_input_Toa0vH=ShowBarPredictions,_27097_input_JYZo0F=UseAtrOffset,_27099_input_4lXnaA=BarPredictionsOffset)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          