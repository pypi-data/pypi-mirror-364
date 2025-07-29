
  
from dataclasses import dataclass
from typing import Optional, Union, Literal, TypedDict, Any, Tuple, List
from datetime import datetime
from qpace import Ctx, Backtest
from qpace_suite import _lib
  
  


def normalize_deriv(ctx: Ctx, src: List[float], quadraticMeanLength: int, ) -> List[float]:
    """
@function Returns the smoothed hyperbolic tangent of the input series.
 @param src <series float> The input series (i.e., the first-order derivative for price).
 @param quadraticMeanLength <int>  The length of the quadratic mean (RMS).
 @returns	nDeriv <series float> The normalized derivative of the input series.

`normalizeDeriv(series<float> src, int quadraticMeanLength) -> float`
    """
    return _lib.Incr_fn_normalizeDeriv_ed238d(ctx=ctx, ).collect(_25853_src=src, _25854_quadraticMeanLength=quadraticMeanLength)

class NormalizeDerivLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class NormalizeDeriv:
    """
@function Returns the smoothed hyperbolic tangent of the input series.
 @param src <series float> The input series (i.e., the first-order derivative for price).
 @param quadraticMeanLength <int>  The length of the quadratic mean (RMS).
 @returns	nDeriv <series float> The normalized derivative of the input series.

`normalizeDeriv(series<float> src, int quadraticMeanLength) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_normalizeDeriv_ed238d(ctx, )
        self.locals = NormalizeDerivLocals(self.inner)

    def next(self, src: float, quadraticMeanLength: int) -> Optional[float]:
        return self.inner.next(_25853_src=src, _25854_quadraticMeanLength=quadraticMeanLength)
    



def normalize(ctx: Ctx, src: List[float], min: float, max: float, ) -> List[float]:
    """
@function Rescales a source value with an unbounded range to a target range.
 @param src <series float> The input series
 @param min <float> The minimum value of the unbounded range
 @param max <float> The maximum value of the unbounded range
 @returns <series float> The normalized series

`normalize(series<float> src, float min, float max) -> float`
    """
    return _lib.Incr_fn_normalize_181e1a(ctx=ctx, ).collect(_25859_src=src, _25860_min=min, _25861_max=max)

class NormalizeLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def _historicMin(self) -> float:
        return self.__inner._25862__historicMin()
  

    @property
    def _historicMax(self) -> float:
        return self.__inner._25863__historicMax()
  
      

class Normalize:
    """
@function Rescales a source value with an unbounded range to a target range.
 @param src <series float> The input series
 @param min <float> The minimum value of the unbounded range
 @param max <float> The maximum value of the unbounded range
 @returns <series float> The normalized series

`normalize(series<float> src, float min, float max) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_normalize_181e1a(ctx, )
        self.locals = NormalizeLocals(self.inner)

    def next(self, src: float, min: float, max: float) -> Optional[float]:
        return self.inner.next(_25859_src=src, _25860_min=min, _25861_max=max)
    



def rescale(ctx: Ctx, src: List[float], oldMin: float, oldMax: float, newMin: float, newMax: float, ) -> List[float]:
    """
@function Rescales a source value with a bounded range to anther bounded range
 @param src <series float> The input series
 @param oldMin <float> The minimum value of the range to rescale from
 @param oldMax <float> The maximum value of the range to rescale from
 @param newMin <float> The minimum value of the range to rescale to
 @param newMax <float> The maximum value of the range to rescale to 
 @returns <series float> The rescaled series

`rescale(series<float> src, float oldMin, float oldMax, float newMin, float newMax) -> float`
    """
    return _lib.Incr_fn_rescale_87a549(ctx=ctx, ).collect(_25865_src=src, _25866_oldMin=oldMin, _25867_oldMax=oldMax, _25868_newMin=newMin, _25869_newMax=newMax)

class RescaleLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Rescale:
    """
@function Rescales a source value with a bounded range to anther bounded range
 @param src <series float> The input series
 @param oldMin <float> The minimum value of the range to rescale from
 @param oldMax <float> The maximum value of the range to rescale from
 @param newMin <float> The minimum value of the range to rescale to
 @param newMax <float> The maximum value of the range to rescale to 
 @returns <series float> The rescaled series

`rescale(series<float> src, float oldMin, float oldMax, float newMin, float newMax) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_rescale_87a549(ctx, )
        self.locals = RescaleLocals(self.inner)

    def next(self, src: float, oldMin: float, oldMax: float, newMin: float, newMax: float) -> Optional[float]:
        return self.inner.next(_25865_src=src, _25866_oldMin=oldMin, _25867_oldMax=oldMax, _25868_newMin=newMin, _25869_newMax=newMax)
    



def color_green(ctx: Ctx, prediction: float, ) -> Tuple[int, int, int, int]:
    """
@function Assigns varying shades of the color green based on the KNN classification
 @param prediction Value (int|float) of the prediction 
 @returns color <color>

`color_green(float prediction) -> color`
    """
    return _lib.Incr_fn_color_green_1021d8(ctx=ctx, ).collect(_25889_prediction=prediction)

class ColorGreenLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class ColorGreen:
    """
@function Assigns varying shades of the color green based on the KNN classification
 @param prediction Value (int|float) of the prediction 
 @returns color <color>

`color_green(float prediction) -> color`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_color_green_1021d8(ctx, )
        self.locals = ColorGreenLocals(self.inner)

    def next(self, prediction: float) -> Optional[Tuple[int, int, int, int]]:
        return self.inner.next(_25889_prediction=prediction)
    



def color_red(ctx: Ctx, prediction: float, ) -> Tuple[int, int, int, int]:
    """
@function Assigns varying shades of the color red based on the KNN classification
 @param prediction Value of the prediction
 @returns color

`color_red(float prediction) -> color`
    """
    return _lib.Incr_fn_color_red_195f01(ctx=ctx, ).collect(_25891_prediction=prediction)

class ColorRedLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class ColorRed:
    """
@function Assigns varying shades of the color red based on the KNN classification
 @param prediction Value of the prediction
 @returns color

`color_red(float prediction) -> color`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_color_red_195f01(ctx, )
        self.locals = ColorRedLocals(self.inner)

    def next(self, prediction: float) -> Optional[Tuple[int, int, int, int]]:
        return self.inner.next(_25891_prediction=prediction)
    



def tanh(ctx: Ctx, src: List[float], ) -> List[float]:
    """
@function Returns the the hyperbolic tangent of the input series. The sigmoid-like hyperbolic tangent function is used to compress the input to a value between -1 and 1.
 @param src <series float> The input series (i.e., the normalized derivative).
 @returns	tanh <series float> The hyperbolic tangent of the input series.

`tanh(series<float> src) -> float`
    """
    return _lib.Incr_fn_tanh_f521c2(ctx=ctx, ).collect(_25893_src=src)

class TanhLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Tanh:
    """
@function Returns the the hyperbolic tangent of the input series. The sigmoid-like hyperbolic tangent function is used to compress the input to a value between -1 and 1.
 @param src <series float> The input series (i.e., the normalized derivative).
 @returns	tanh <series float> The hyperbolic tangent of the input series.

`tanh(series<float> src) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_tanh_f521c2(ctx, )
        self.locals = TanhLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_25893_src=src)
    



def dual_pole_filter(ctx: Ctx, src: List[float], lookback: int, ) -> List[float]:
    """
@function Returns the smoothed hyperbolic tangent of the input series.
@param src <series float> The input series (i.e., the hyperbolic tangent).
@param lookback <int> The lookback window for the smoothing.
@returns filter <series float> The smoothed hyperbolic tangent of the input series.

`dualPoleFilter(series<float> src, int lookback) -> float`
    """
    return _lib.Incr_fn_dualPoleFilter_596ae2(ctx=ctx, ).collect(_25896_src=src, _25897_lookback=lookback)

class DualPoleFilterLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class DualPoleFilter:
    """
@function Returns the smoothed hyperbolic tangent of the input series.
@param src <series float> The input series (i.e., the hyperbolic tangent).
@param lookback <int> The lookback window for the smoothing.
@returns filter <series float> The smoothed hyperbolic tangent of the input series.

`dualPoleFilter(series<float> src, int lookback) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_dualPoleFilter_596ae2(ctx, )
        self.locals = DualPoleFilterLocals(self.inner)

    def next(self, src: float, lookback: int) -> Optional[float]:
        return self.inner.next(_25896_src=src, _25897_lookback=lookback)
    



def tanh_transform(ctx: Ctx, src: List[float], smoothingFrequency: int, quadraticMeanLength: int, ) -> List[float]:
    """
@function Returns the tanh transform of the input series.
 @param src <series float> The input series (i.e., the result of the tanh calculation).
 @param lookback <int> The lookback window for the smoothing.
 @returns signal <series float> The smoothed hyperbolic tangent transform of the input series.

`tanhTransform(series<float> src, int smoothingFrequency, int quadraticMeanLength) -> float`
    """
    return _lib.Incr_fn_tanhTransform_3d50ee(ctx=ctx, ).collect(_25906_src=src, _25907_smoothingFrequency=smoothingFrequency, _25908_quadraticMeanLength=quadraticMeanLength)

class TanhTransformLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class TanhTransform:
    """
@function Returns the tanh transform of the input series.
 @param src <series float> The input series (i.e., the result of the tanh calculation).
 @param lookback <int> The lookback window for the smoothing.
 @returns signal <series float> The smoothed hyperbolic tangent transform of the input series.

`tanhTransform(series<float> src, int smoothingFrequency, int quadraticMeanLength) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_tanhTransform_3d50ee(ctx, )
        self.locals = TanhTransformLocals(self.inner)

    def next(self, src: float, smoothingFrequency: int, quadraticMeanLength: int) -> Optional[float]:
        return self.inner.next(_25906_src=src, _25907_smoothingFrequency=smoothingFrequency, _25908_quadraticMeanLength=quadraticMeanLength)
    



def n_rsi(ctx: Ctx, src: List[float], n1: int, n2: int, ) -> List[float]:
    """
@function Returns the normalized RSI ideal for use in ML algorithms.
 @param src <series float> The input series (i.e., the result of the RSI calculation).
 @param n1 <int> The length of the RSI.
 @param n2 <int> The smoothing length of the RSI.
 @returns signal <series float> The normalized RSI.

`n_rsi(series<float> src, int n1, int n2) -> float`
    """
    return _lib.Incr_fn_n_rsi_4fa39d(ctx=ctx, ).collect(_25911_src=src, _25912_n1=n1, _25913_n2=n2)

class NRsiLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class NRsi:
    """
@function Returns the normalized RSI ideal for use in ML algorithms.
 @param src <series float> The input series (i.e., the result of the RSI calculation).
 @param n1 <int> The length of the RSI.
 @param n2 <int> The smoothing length of the RSI.
 @returns signal <series float> The normalized RSI.

`n_rsi(series<float> src, int n1, int n2) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_n_rsi_4fa39d(ctx, )
        self.locals = NRsiLocals(self.inner)

    def next(self, src: float, n1: int, n2: int) -> Optional[float]:
        return self.inner.next(_25911_src=src, _25912_n1=n1, _25913_n2=n2)
    



def n_cci(ctx: Ctx, src: List[float], n1: int, n2: int, ) -> List[float]:
    """
@function Returns the normalized CCI ideal for use in ML algorithms.
 @param src <series float> The input series (i.e., the result of the CCI calculation).
 @param n1 <int> The length of the CCI.
 @param n2 <int> The smoothing length of the CCI.
 @returns signal <series float> The normalized CCI.

`n_cci(series<float> src, int n1, int n2) -> float`
    """
    return _lib.Incr_fn_n_cci_36e5b0(ctx=ctx, ).collect(_25915_src=src, _25916_n1=n1, _25917_n2=n2)

class NCciLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class NCci:
    """
@function Returns the normalized CCI ideal for use in ML algorithms.
 @param src <series float> The input series (i.e., the result of the CCI calculation).
 @param n1 <int> The length of the CCI.
 @param n2 <int> The smoothing length of the CCI.
 @returns signal <series float> The normalized CCI.

`n_cci(series<float> src, int n1, int n2) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_n_cci_36e5b0(ctx, )
        self.locals = NCciLocals(self.inner)

    def next(self, src: float, n1: int, n2: int) -> Optional[float]:
        return self.inner.next(_25915_src=src, _25916_n1=n1, _25917_n2=n2)
    



def n_wt(ctx: Ctx, src: List[float], n1: Optional[int] = None, n2: Optional[int] = None, ) -> List[float]:
    """
@function Returns the normalized WaveTrend Classic series ideal for use in ML algorithms.
 @param src <series float> The input series (i.e., the result of the WaveTrend Classic calculation).
 @param paramA <int> The first smoothing length for WaveTrend Classic.
 @param paramB <int> The second smoothing length for the WaveTrend Classic.
 @param transformLength <int> The length of the transform.
 @returns signal <series float> The normalized WaveTrend Classic series.

`n_wt(series<float> src, int n1 = 10, int n2 = 11) -> float`
    """
    return _lib.Incr_fn_n_wt_dabb7a(ctx=ctx, ).collect(_25919_src=src, _25920_n1=n1, _25921_n2=n2)

class NWtLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class NWt:
    """
@function Returns the normalized WaveTrend Classic series ideal for use in ML algorithms.
 @param src <series float> The input series (i.e., the result of the WaveTrend Classic calculation).
 @param paramA <int> The first smoothing length for WaveTrend Classic.
 @param paramB <int> The second smoothing length for the WaveTrend Classic.
 @param transformLength <int> The length of the transform.
 @returns signal <series float> The normalized WaveTrend Classic series.

`n_wt(series<float> src, int n1 = 10, int n2 = 11) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_n_wt_dabb7a(ctx, )
        self.locals = NWtLocals(self.inner)

    def next(self, src: float, n1: Optional[int] = None, n2: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_25919_src=src, _25920_n1=n1, _25921_n2=n2)
    



def n_adx(ctx: Ctx, highSrc: List[float], lowSrc: List[float], closeSrc: List[float], n1: int, ) -> List[float]:
    """
@function Returns the normalized ADX ideal for use in ML algorithms.
 @param highSrc <series float> The input series for the high price.
 @param lowSrc <series float> The input series for the low price.
 @param closeSrc <series float> The input series for the close price.
 @param n1 <int> The length of the ADX.

`n_adx(series<float> highSrc, series<float> lowSrc, series<float> closeSrc, int n1) -> float`
    """
    return _lib.Incr_fn_n_adx_0a22bf(ctx=ctx, ).collect(_25928_highSrc=highSrc, _25929_lowSrc=lowSrc, _25930_closeSrc=closeSrc, _25931_n1=n1)

class NAdxLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class NAdx:
    """
@function Returns the normalized ADX ideal for use in ML algorithms.
 @param highSrc <series float> The input series for the high price.
 @param lowSrc <series float> The input series for the low price.
 @param closeSrc <series float> The input series for the close price.
 @param n1 <int> The length of the ADX.

`n_adx(series<float> highSrc, series<float> lowSrc, series<float> closeSrc, int n1) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_n_adx_0a22bf(ctx, )
        self.locals = NAdxLocals(self.inner)

    def next(self, highSrc: float, lowSrc: float, closeSrc: float, n1: int) -> Optional[float]:
        return self.inner.next(_25928_highSrc=highSrc, _25929_lowSrc=lowSrc, _25930_closeSrc=closeSrc, _25931_n1=n1)
    



def regime_filter(ctx: Ctx, src: Optional[List[float]] = None, threshold: Optional[float] = None, useRegimeFilter: Optional[bool] = None, ) -> List[bool]:
    """
# @regime_filter
 # @param src <series float> The source series.
 # @param threshold <float> The threshold.
 # @param useRegimeFilter <bool> Whether to use the regime filter.
 # @returns <bool> Boolean indicating whether or not to let the signal pass through the filter.

`regime_filter(series<float> src = ohlc4, float threshold, bool useRegimeFilter) -> bool`
    """
    return _lib.Incr_fn_regime_filter_9bbaf3(ctx=ctx, ).collect(_25945_src=src, _25946_threshold=threshold, _25947_useRegimeFilter=useRegimeFilter)

class RegimeFilterLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class RegimeFilter:
    """
# @regime_filter
 # @param src <series float> The source series.
 # @param threshold <float> The threshold.
 # @param useRegimeFilter <bool> Whether to use the regime filter.
 # @returns <bool> Boolean indicating whether or not to let the signal pass through the filter.

`regime_filter(series<float> src = ohlc4, float threshold, bool useRegimeFilter) -> bool`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_regime_filter_9bbaf3(ctx, )
        self.locals = RegimeFilterLocals(self.inner)

    def next(self, src: Optional[float] = None, threshold: Optional[float] = None, useRegimeFilter: Optional[bool] = None) -> Optional[bool]:
        return self.inner.next(_25945_src=src, _25946_threshold=threshold, _25947_useRegimeFilter=useRegimeFilter)
    



def filter_adx(ctx: Ctx, src: Optional[List[float]] = None, length: Optional[int] = None, adxThreshold: Optional[int] = None, useAdxFilter: Optional[bool] = None, ) -> List[bool]:
    """
@function filter_adx
 @param src <series float> The source series.
 @param length <int> The length of the ADX.
 @param adxThreshold <int> The ADX threshold.
 @param useAdxFilter <bool> Whether to use the ADX filter.
 @returns <series float> The ADX.

`filter_adx(series<float> src = close, int length = 14, int adxThreshold, bool useAdxFilter) -> bool`
    """
    return _lib.Incr_fn_filter_adx_3eb18b(ctx=ctx, ).collect(_25957_src=src, _25958_length=length, _25959_adxThreshold=adxThreshold, _25960_useAdxFilter=useAdxFilter)

class FilterAdxLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class FilterAdx:
    """
@function filter_adx
 @param src <series float> The source series.
 @param length <int> The length of the ADX.
 @param adxThreshold <int> The ADX threshold.
 @param useAdxFilter <bool> Whether to use the ADX filter.
 @returns <series float> The ADX.

`filter_adx(series<float> src = close, int length = 14, int adxThreshold, bool useAdxFilter) -> bool`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_filter_adx_3eb18b(ctx, )
        self.locals = FilterAdxLocals(self.inner)

    def next(self, src: Optional[float] = None, length: Optional[int] = None, adxThreshold: Optional[int] = None, useAdxFilter: Optional[bool] = None) -> Optional[bool]:
        return self.inner.next(_25957_src=src, _25958_length=length, _25959_adxThreshold=adxThreshold, _25960_useAdxFilter=useAdxFilter)
    



def filter_volatility(ctx: Ctx, minLength: Optional[int] = None, maxLength: Optional[int] = None, useVolatilityFilter: Optional[bool] = None, ) -> List[bool]:
    """
@function filter_volatility
 @param minLength <int> The minimum length of the ATR.
 @param maxLength <int> The maximum length of the ATR.
 @param useVolatilityFilter <bool> Whether to use the volatility filter.
 @returns <bool> Boolean indicating whether or not to let the signal pass through the filter.

`filter_volatility(int minLength = 1, int maxLength = 10, bool useVolatilityFilter) -> bool`
    """
    return _lib.Incr_fn_filter_volatility_eb48ac(ctx=ctx, ).collect(_25972_minLength=minLength, _25973_maxLength=maxLength, _25974_useVolatilityFilter=useVolatilityFilter)

class FilterVolatilityLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class FilterVolatility:
    """
@function filter_volatility
 @param minLength <int> The minimum length of the ATR.
 @param maxLength <int> The maximum length of the ATR.
 @param useVolatilityFilter <bool> Whether to use the volatility filter.
 @returns <bool> Boolean indicating whether or not to let the signal pass through the filter.

`filter_volatility(int minLength = 1, int maxLength = 10, bool useVolatilityFilter) -> bool`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_filter_volatility_eb48ac(ctx, )
        self.locals = FilterVolatilityLocals(self.inner)

    def next(self, minLength: Optional[int] = None, maxLength: Optional[int] = None, useVolatilityFilter: Optional[bool] = None) -> Optional[bool]:
        return self.inner.next(_25972_minLength=minLength, _25973_maxLength=maxLength, _25974_useVolatilityFilter=useVolatilityFilter)
    



def backtest(ctx: Ctx, high: List[float], low: List[float], open: List[float], startLongTrade: List[bool], endLongTrade: List[bool], startShortTrade: List[bool], endShortTrade: List[bool], isEarlySignalFlip: List[bool], maxBarsBackIndex: int, thisBarIndex: int, src: List[float], useWorstCase: bool, ) -> Tuple[float, float, float, float, str, float, float]:
    """
@function Performs a basic backtest using the specified parameters and conditions.
 @param high <series float> The input series for the high price.
 @param low <series float> The input series for the low price.
 @param open <series float> The input series for the open price.
 @param startLongTrade <series bool> The series of conditions that indicate the start of a long trade.
 @param endLongTrade <series bool> The series of conditions that indicate the end of a long trade.
 @param startShortTrade <series bool> The series of conditions that indicate the start of a short trade.
 @param endShortTrade <series bool> The series of conditions that indicate the end of a short trade.
 @param isEarlySignalFlip <bool> Whether or not the signal flip is early.
 @param maxBarsBackIndex <int> The maximum number of bars to go back in the backtest.
 @param thisBarIndex <int> The current bar index.
 @param src <series float> The source series.
 @param useWorstCase <bool> Whether to use the worst case scenario for the backtest.
 @returns <tuple strings> A tuple containing backtest values

`backtest(series<float> high, series<float> low, series<float> open, series<bool> startLongTrade, series<bool> endLongTrade, series<bool> startShortTrade, series<bool> endShortTrade, series<bool> isEarlySignalFlip, int maxBarsBackIndex, int thisBarIndex, series<float> src, bool useWorstCase) -> [float, float, float, float, string, float, float]`
    """
    return _lib.Incr_fn_backtest_7d28ad(ctx=ctx, ).collect(_25978_high=high, _25979_low=low, _25980_open=open, _25981_startLongTrade=startLongTrade, _25982_endLongTrade=endLongTrade, _25983_startShortTrade=startShortTrade, _25984_endShortTrade=endShortTrade, _25985_isEarlySignalFlip=isEarlySignalFlip, _25986_maxBarsBackIndex=maxBarsBackIndex, _25987_thisBarIndex=thisBarIndex, _25988_src=src, _25989_useWorstCase=useWorstCase)

class BacktestLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def start_long_trade(self) -> float:
        return self.__inner._25991_start_long_trade()
  

    @property
    def start_short_trade(self) -> float:
        return self.__inner._25992_start_short_trade()
  

    @property
    def total_short_profit(self) -> float:
        return self.__inner._25993_total_short_profit()
  

    @property
    def total_long_profit(self) -> float:
        return self.__inner._25994_total_long_profit()
  

    @property
    def wins(self) -> int:
        return self.__inner._25995_wins()
  

    @property
    def losses(self) -> int:
        return self.__inner._25996_losses()
  

    @property
    def trade_count(self) -> int:
        return self.__inner._25997_trade_count()
  

    @property
    def early_signal_flip_count(self) -> int:
        return self.__inner._25998_early_signal_flip_count()
  

    @property
    def tookProfit(self) -> bool:
        return self.__inner._25999_tookProfit()
  
      

class Backtest:
    """
@function Performs a basic backtest using the specified parameters and conditions.
 @param high <series float> The input series for the high price.
 @param low <series float> The input series for the low price.
 @param open <series float> The input series for the open price.
 @param startLongTrade <series bool> The series of conditions that indicate the start of a long trade.
 @param endLongTrade <series bool> The series of conditions that indicate the end of a long trade.
 @param startShortTrade <series bool> The series of conditions that indicate the start of a short trade.
 @param endShortTrade <series bool> The series of conditions that indicate the end of a short trade.
 @param isEarlySignalFlip <bool> Whether or not the signal flip is early.
 @param maxBarsBackIndex <int> The maximum number of bars to go back in the backtest.
 @param thisBarIndex <int> The current bar index.
 @param src <series float> The source series.
 @param useWorstCase <bool> Whether to use the worst case scenario for the backtest.
 @returns <tuple strings> A tuple containing backtest values

`backtest(series<float> high, series<float> low, series<float> open, series<bool> startLongTrade, series<bool> endLongTrade, series<bool> startShortTrade, series<bool> endShortTrade, series<bool> isEarlySignalFlip, int maxBarsBackIndex, int thisBarIndex, series<float> src, bool useWorstCase) -> [float, float, float, float, string, float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_backtest_7d28ad(ctx, )
        self.locals = BacktestLocals(self.inner)

    def next(self, high: float, low: float, open: float, startLongTrade: bool, endLongTrade: bool, startShortTrade: bool, endShortTrade: bool, isEarlySignalFlip: bool, maxBarsBackIndex: int, thisBarIndex: int, src: float, useWorstCase: bool) -> Optional[Tuple[float, float, float, float, str, float, float]]:
        return self.inner.next(_25978_high=high, _25979_low=low, _25980_open=open, _25981_startLongTrade=startLongTrade, _25982_endLongTrade=endLongTrade, _25983_startShortTrade=startShortTrade, _25984_endShortTrade=endShortTrade, _25985_isEarlySignalFlip=isEarlySignalFlip, _25986_maxBarsBackIndex=maxBarsBackIndex, _25987_thisBarIndex=thisBarIndex, _25988_src=src, _25989_useWorstCase=useWorstCase)
    


class MainAlert(TypedDict):
    time: datetime
    bar_index: int
    title: Optional[str]
    message: Optional[str]

class MainResultLocals(TypedDict):

    pass

class MainResult(TypedDict):
    alerts: List[MainAlert]
    locals: MainResultLocals


def main(ctx: Ctx, ) -> MainResult:
    """
`main() -> void`
    """
    return _lib.Incr_fn_main_b60e86(ctx=ctx, ).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_b60e86(ctx, )
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          