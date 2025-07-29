
  
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
    return _lib.Incr_fn_main_6b4ad7(ctx=ctx, _29904_input_zhk3rN=generalSettingsSource,_29906_input_Su2sxU=generalSettingsNeighborsCount,_29908_input_C76dvy=generalSettingsMaxBarsBack,_29910_input_COIqFT=featureEngineeringFeatureCount,_29912_input_fU3Jgm=generalSettingsColorCompression,_29914_input_hLJGRJ=exitsGeneralSettingsShowDefaultExits,_29916_input_pHmk7A=exitsGeneralSettingsUseDynamicExits,_29919_input_iOLFJP=ShowTradeStats,_29921_input_YFxg76=UseWorstCase,_29923_input_EPwCbs=filtersUseVolatilityFilter,_29925_input_o99MM1=regimeFiltersUseRegimeFilter,_29927_input_m8T9fP=adxFiltersUseAdxFilter,_29929_input_Ow52q5=regimeFiltersThreshold,_29931_input_bOOgfK=adxFiltersThreshold,_29938_input_Elspa2=F1String,_29940_input_0ahgzZ=F1ParamA,_29942_input_LPfIUy=F1ParamB,_29944_input_E3W561=F2String,_29946_input_8jam00=F2ParamA,_29948_input_ljiz9h=F2ParamB,_29950_input_8RlOK7=F3String,_29952_input_PPme79=F3ParamA,_29954_input_XtZwUC=F3ParamB,_29956_input_4NVTac=F4String,_29958_input_n5PPLS=F4ParamA,_29960_input_IrceNr=F4ParamB,_29962_input_mC3kh0=F5String,_29964_input_PFwcjF=F5ParamA,_29966_input_AX2VhF=F5ParamB,_29986_input_Qep4RN=UseEmaFilter,_29988_input_d5Mu3b=EmaPeriod,_29992_input_Xkgpv9=UseSmaFilter,_29994_input_wCj5As=SmaPeriod,_29998_input_nGW3Wg=UseKernelFilter,_30000_input_QU5SFi=ShowKernelEstimate,_30002_input_dUIfN0=UseKernelSmoothing,_30004_input_IRoZNB=H,_30006_input_wRmGNW=R,_30008_input_lK4Mkp=X,_30010_input_VTkPEx=Lag,_30012_input_4AUVdY=ShowBarColors,_30014_input_5SPARq=ShowBarPredictions,_30016_input_PiLLQu=UseAtrOffset,_30018_input_CzDcYP=BarPredictionsOffset).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def prediction(self) -> float:
        return self.__inner._29089_prediction()
  

    @property
    def signal(self) -> int:
        return self.__inner._29090_signal()
  

    @property
    def barsHeld(self) -> int:
        return self.__inner._29098_barsHeld()
  

    @property
    def kernelEstimate(self) -> float:
        return self.__inner._29114_kernelEstimate()
  

    @property
    def startLongTrade(self) -> bool:
        return self.__inner._29132_startLongTrade()
  

    @property
    def startShortTrade(self) -> bool:
        return self.__inner._29133_startShortTrade()
  

    @property
    def endLongTrade(self) -> bool:
        return self.__inner._29147_endLongTrade()
  

    @property
    def endShortTrade(self) -> bool:
        return self.__inner._29148_endShortTrade()
  

    @property
    def backTestStream(self) -> int:
        return self.__inner._29156_backTestStream()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, generalSettingsSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, generalSettingsNeighborsCount: Optional[int] = None, generalSettingsMaxBarsBack: Optional[int] = None, featureEngineeringFeatureCount: Optional[int] = None, generalSettingsColorCompression: Optional[int] = None, exitsGeneralSettingsShowDefaultExits: Optional[bool] = None, exitsGeneralSettingsUseDynamicExits: Optional[bool] = None, ShowTradeStats: Optional[bool] = None, UseWorstCase: Optional[bool] = None, filtersUseVolatilityFilter: Optional[bool] = None, regimeFiltersUseRegimeFilter: Optional[bool] = None, adxFiltersUseAdxFilter: Optional[bool] = None, regimeFiltersThreshold: Optional[float] = None, adxFiltersThreshold: Optional[int] = None, F1String: Optional[str] = None, F1ParamA: Optional[int] = None, F1ParamB: Optional[int] = None, F2String: Optional[str] = None, F2ParamA: Optional[int] = None, F2ParamB: Optional[int] = None, F3String: Optional[str] = None, F3ParamA: Optional[int] = None, F3ParamB: Optional[int] = None, F4String: Optional[str] = None, F4ParamA: Optional[int] = None, F4ParamB: Optional[int] = None, F5String: Optional[str] = None, F5ParamA: Optional[int] = None, F5ParamB: Optional[int] = None, UseEmaFilter: Optional[bool] = None, EmaPeriod: Optional[int] = None, UseSmaFilter: Optional[bool] = None, SmaPeriod: Optional[int] = None, UseKernelFilter: Optional[bool] = None, ShowKernelEstimate: Optional[bool] = None, UseKernelSmoothing: Optional[bool] = None, H: Optional[int] = None, R: Optional[float] = None, X: Optional[int] = None, Lag: Optional[int] = None, ShowBarColors: Optional[bool] = None, ShowBarPredictions: Optional[bool] = None, UseAtrOffset: Optional[bool] = None, BarPredictionsOffset: Optional[float] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_6b4ad7(ctx, _29904_input_zhk3rN=generalSettingsSource,_29906_input_Su2sxU=generalSettingsNeighborsCount,_29908_input_C76dvy=generalSettingsMaxBarsBack,_29910_input_COIqFT=featureEngineeringFeatureCount,_29912_input_fU3Jgm=generalSettingsColorCompression,_29914_input_hLJGRJ=exitsGeneralSettingsShowDefaultExits,_29916_input_pHmk7A=exitsGeneralSettingsUseDynamicExits,_29919_input_iOLFJP=ShowTradeStats,_29921_input_YFxg76=UseWorstCase,_29923_input_EPwCbs=filtersUseVolatilityFilter,_29925_input_o99MM1=regimeFiltersUseRegimeFilter,_29927_input_m8T9fP=adxFiltersUseAdxFilter,_29929_input_Ow52q5=regimeFiltersThreshold,_29931_input_bOOgfK=adxFiltersThreshold,_29938_input_Elspa2=F1String,_29940_input_0ahgzZ=F1ParamA,_29942_input_LPfIUy=F1ParamB,_29944_input_E3W561=F2String,_29946_input_8jam00=F2ParamA,_29948_input_ljiz9h=F2ParamB,_29950_input_8RlOK7=F3String,_29952_input_PPme79=F3ParamA,_29954_input_XtZwUC=F3ParamB,_29956_input_4NVTac=F4String,_29958_input_n5PPLS=F4ParamA,_29960_input_IrceNr=F4ParamB,_29962_input_mC3kh0=F5String,_29964_input_PFwcjF=F5ParamA,_29966_input_AX2VhF=F5ParamB,_29986_input_Qep4RN=UseEmaFilter,_29988_input_d5Mu3b=EmaPeriod,_29992_input_Xkgpv9=UseSmaFilter,_29994_input_wCj5As=SmaPeriod,_29998_input_nGW3Wg=UseKernelFilter,_30000_input_QU5SFi=ShowKernelEstimate,_30002_input_dUIfN0=UseKernelSmoothing,_30004_input_IRoZNB=H,_30006_input_wRmGNW=R,_30008_input_lK4Mkp=X,_30010_input_VTkPEx=Lag,_30012_input_4AUVdY=ShowBarColors,_30014_input_5SPARq=ShowBarPredictions,_30016_input_PiLLQu=UseAtrOffset,_30018_input_CzDcYP=BarPredictionsOffset)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          