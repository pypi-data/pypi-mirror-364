
  
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
    return _lib.Incr_fn_normalizeDeriv_22d897(ctx=ctx, ).collect(_22934_src=src, _22935_quadraticMeanLength=quadraticMeanLength)

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
        self.inner = _lib.Incr_fn_normalizeDeriv_22d897(ctx, )
        self.locals = NormalizeDerivLocals(self.inner)

    def next(self, src: float, quadraticMeanLength: int) -> Optional[float]:
        return self.inner.next(_22934_src=src, _22935_quadraticMeanLength=quadraticMeanLength)
    



def normalize(ctx: Ctx, src: List[float], min: float, max: float, ) -> List[float]:
    """
@function Rescales a source value with an unbounded range to a target range.
 @param src <series float> The input series
 @param min <float> The minimum value of the unbounded range
 @param max <float> The maximum value of the unbounded range
 @returns <series float> The normalized series

`normalize(series<float> src, float min, float max) -> float`
    """
    return _lib.Incr_fn_normalize_25c3b0(ctx=ctx, ).collect(_22940_src=src, _22941_min=min, _22942_max=max)

class NormalizeLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def _historicMin(self) -> float:
        return self.__inner._22943__historicMin()
  

    @property
    def _historicMax(self) -> float:
        return self.__inner._22944__historicMax()
  
      

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
        self.inner = _lib.Incr_fn_normalize_25c3b0(ctx, )
        self.locals = NormalizeLocals(self.inner)

    def next(self, src: float, min: float, max: float) -> Optional[float]:
        return self.inner.next(_22940_src=src, _22941_min=min, _22942_max=max)
    



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
    return _lib.Incr_fn_rescale_7c8ff1(ctx=ctx, ).collect(_22946_src=src, _22947_oldMin=oldMin, _22948_oldMax=oldMax, _22949_newMin=newMin, _22950_newMax=newMax)

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
        self.inner = _lib.Incr_fn_rescale_7c8ff1(ctx, )
        self.locals = RescaleLocals(self.inner)

    def next(self, src: float, oldMin: float, oldMax: float, newMin: float, newMax: float) -> Optional[float]:
        return self.inner.next(_22946_src=src, _22947_oldMin=oldMin, _22948_oldMax=oldMax, _22949_newMin=newMin, _22950_newMax=newMax)
    



def color_green(ctx: Ctx, prediction: float, ) -> Tuple[int, int, int, int]:
    """
@function Assigns varying shades of the color green based on the KNN classification
 @param prediction Value (int|float) of the prediction 
 @returns color <color>

`color_green(float prediction) -> color`
    """
    return _lib.Incr_fn_color_green_4d10a2(ctx=ctx, ).collect(_22970_prediction=prediction)

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
        self.inner = _lib.Incr_fn_color_green_4d10a2(ctx, )
        self.locals = ColorGreenLocals(self.inner)

    def next(self, prediction: float) -> Optional[Tuple[int, int, int, int]]:
        return self.inner.next(_22970_prediction=prediction)
    



def color_red(ctx: Ctx, prediction: float, ) -> Tuple[int, int, int, int]:
    """
@function Assigns varying shades of the color red based on the KNN classification
 @param prediction Value of the prediction
 @returns color

`color_red(float prediction) -> color`
    """
    return _lib.Incr_fn_color_red_1e053d(ctx=ctx, ).collect(_22972_prediction=prediction)

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
        self.inner = _lib.Incr_fn_color_red_1e053d(ctx, )
        self.locals = ColorRedLocals(self.inner)

    def next(self, prediction: float) -> Optional[Tuple[int, int, int, int]]:
        return self.inner.next(_22972_prediction=prediction)
    



def tanh(ctx: Ctx, src: List[float], ) -> List[float]:
    """
@function Returns the the hyperbolic tangent of the input series. The sigmoid-like hyperbolic tangent function is used to compress the input to a value between -1 and 1.
 @param src <series float> The input series (i.e., the normalized derivative).
 @returns	tanh <series float> The hyperbolic tangent of the input series.

`tanh(series<float> src) -> float`
    """
    return _lib.Incr_fn_tanh_413550(ctx=ctx, ).collect(_22974_src=src)

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
        self.inner = _lib.Incr_fn_tanh_413550(ctx, )
        self.locals = TanhLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_22974_src=src)
    



def dual_pole_filter(ctx: Ctx, src: List[float], lookback: int, ) -> List[float]:
    """
@function Returns the smoothed hyperbolic tangent of the input series.
@param src <series float> The input series (i.e., the hyperbolic tangent).
@param lookback <int> The lookback window for the smoothing.
@returns filter <series float> The smoothed hyperbolic tangent of the input series.

`dualPoleFilter(series<float> src, int lookback) -> float`
    """
    return _lib.Incr_fn_dualPoleFilter_1700c0(ctx=ctx, ).collect(_22977_src=src, _22978_lookback=lookback)

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
        self.inner = _lib.Incr_fn_dualPoleFilter_1700c0(ctx, )
        self.locals = DualPoleFilterLocals(self.inner)

    def next(self, src: float, lookback: int) -> Optional[float]:
        return self.inner.next(_22977_src=src, _22978_lookback=lookback)
    



def tanh_transform(ctx: Ctx, src: List[float], smoothingFrequency: int, quadraticMeanLength: int, ) -> List[float]:
    """
@function Returns the tanh transform of the input series.
 @param src <series float> The input series (i.e., the result of the tanh calculation).
 @param lookback <int> The lookback window for the smoothing.
 @returns signal <series float> The smoothed hyperbolic tangent transform of the input series.

`tanhTransform(series<float> src, int smoothingFrequency, int quadraticMeanLength) -> float`
    """
    return _lib.Incr_fn_tanhTransform_62b565(ctx=ctx, ).collect(_22987_src=src, _22988_smoothingFrequency=smoothingFrequency, _22989_quadraticMeanLength=quadraticMeanLength)

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
        self.inner = _lib.Incr_fn_tanhTransform_62b565(ctx, )
        self.locals = TanhTransformLocals(self.inner)

    def next(self, src: float, smoothingFrequency: int, quadraticMeanLength: int) -> Optional[float]:
        return self.inner.next(_22987_src=src, _22988_smoothingFrequency=smoothingFrequency, _22989_quadraticMeanLength=quadraticMeanLength)
    



def n_rsi(ctx: Ctx, src: List[float], n1: int, n2: int, ) -> List[float]:
    """
@function Returns the normalized RSI ideal for use in ML algorithms.
 @param src <series float> The input series (i.e., the result of the RSI calculation).
 @param n1 <int> The length of the RSI.
 @param n2 <int> The smoothing length of the RSI.
 @returns signal <series float> The normalized RSI.

`n_rsi(series<float> src, int n1, int n2) -> float`
    """
    return _lib.Incr_fn_n_rsi_b5dcbe(ctx=ctx, ).collect(_22992_src=src, _22993_n1=n1, _22994_n2=n2)

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
        self.inner = _lib.Incr_fn_n_rsi_b5dcbe(ctx, )
        self.locals = NRsiLocals(self.inner)

    def next(self, src: float, n1: int, n2: int) -> Optional[float]:
        return self.inner.next(_22992_src=src, _22993_n1=n1, _22994_n2=n2)
    



def n_cci(ctx: Ctx, src: List[float], n1: int, n2: int, ) -> List[float]:
    """
@function Returns the normalized CCI ideal for use in ML algorithms.
 @param src <series float> The input series (i.e., the result of the CCI calculation).
 @param n1 <int> The length of the CCI.
 @param n2 <int> The smoothing length of the CCI.
 @returns signal <series float> The normalized CCI.

`n_cci(series<float> src, int n1, int n2) -> float`
    """
    return _lib.Incr_fn_n_cci_157dda(ctx=ctx, ).collect(_22996_src=src, _22997_n1=n1, _22998_n2=n2)

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
        self.inner = _lib.Incr_fn_n_cci_157dda(ctx, )
        self.locals = NCciLocals(self.inner)

    def next(self, src: float, n1: int, n2: int) -> Optional[float]:
        return self.inner.next(_22996_src=src, _22997_n1=n1, _22998_n2=n2)
    



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
    return _lib.Incr_fn_n_wt_6fbc51(ctx=ctx, ).collect(_23000_src=src, _23001_n1=n1, _23002_n2=n2)

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
        self.inner = _lib.Incr_fn_n_wt_6fbc51(ctx, )
        self.locals = NWtLocals(self.inner)

    def next(self, src: float, n1: Optional[int] = None, n2: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_23000_src=src, _23001_n1=n1, _23002_n2=n2)
    



def n_adx(ctx: Ctx, highSrc: List[float], lowSrc: List[float], closeSrc: List[float], n1: int, ) -> List[float]:
    """
@function Returns the normalized ADX ideal for use in ML algorithms.
 @param highSrc <series float> The input series for the high price.
 @param lowSrc <series float> The input series for the low price.
 @param closeSrc <series float> The input series for the close price.
 @param n1 <int> The length of the ADX.

`n_adx(series<float> highSrc, series<float> lowSrc, series<float> closeSrc, int n1) -> float`
    """
    return _lib.Incr_fn_n_adx_73d444(ctx=ctx, ).collect(_23009_highSrc=highSrc, _23010_lowSrc=lowSrc, _23011_closeSrc=closeSrc, _23012_n1=n1)

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
        self.inner = _lib.Incr_fn_n_adx_73d444(ctx, )
        self.locals = NAdxLocals(self.inner)

    def next(self, highSrc: float, lowSrc: float, closeSrc: float, n1: int) -> Optional[float]:
        return self.inner.next(_23009_highSrc=highSrc, _23010_lowSrc=lowSrc, _23011_closeSrc=closeSrc, _23012_n1=n1)
    



def regime_filter(ctx: Ctx, src: Optional[List[float]] = None, threshold: Optional[float] = None, useRegimeFilter: Optional[bool] = None, ) -> List[bool]:
    """
# @regime_filter
 # @param src <series float> The source series.
 # @param threshold <float> The threshold.
 # @param useRegimeFilter <bool> Whether to use the regime filter.
 # @returns <bool> Boolean indicating whether or not to let the signal pass through the filter.

`regime_filter(series<float> src = ohlc4, float threshold, bool useRegimeFilter) -> bool`
    """
    return _lib.Incr_fn_regime_filter_b1bca6(ctx=ctx, ).collect(_23026_src=src, _23027_threshold=threshold, _23028_useRegimeFilter=useRegimeFilter)

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
        self.inner = _lib.Incr_fn_regime_filter_b1bca6(ctx, )
        self.locals = RegimeFilterLocals(self.inner)

    def next(self, src: Optional[float] = None, threshold: Optional[float] = None, useRegimeFilter: Optional[bool] = None) -> Optional[bool]:
        return self.inner.next(_23026_src=src, _23027_threshold=threshold, _23028_useRegimeFilter=useRegimeFilter)
    



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
    return _lib.Incr_fn_filter_adx_bd2ede(ctx=ctx, ).collect(_23038_src=src, _23039_length=length, _23040_adxThreshold=adxThreshold, _23041_useAdxFilter=useAdxFilter)

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
        self.inner = _lib.Incr_fn_filter_adx_bd2ede(ctx, )
        self.locals = FilterAdxLocals(self.inner)

    def next(self, src: Optional[float] = None, length: Optional[int] = None, adxThreshold: Optional[int] = None, useAdxFilter: Optional[bool] = None) -> Optional[bool]:
        return self.inner.next(_23038_src=src, _23039_length=length, _23040_adxThreshold=adxThreshold, _23041_useAdxFilter=useAdxFilter)
    



def filter_volatility(ctx: Ctx, minLength: Optional[int] = None, maxLength: Optional[int] = None, useVolatilityFilter: Optional[bool] = None, ) -> List[bool]:
    """
@function filter_volatility
 @param minLength <int> The minimum length of the ATR.
 @param maxLength <int> The maximum length of the ATR.
 @param useVolatilityFilter <bool> Whether to use the volatility filter.
 @returns <bool> Boolean indicating whether or not to let the signal pass through the filter.

`filter_volatility(int minLength = 1, int maxLength = 10, bool useVolatilityFilter) -> bool`
    """
    return _lib.Incr_fn_filter_volatility_269144(ctx=ctx, ).collect(_23053_minLength=minLength, _23054_maxLength=maxLength, _23055_useVolatilityFilter=useVolatilityFilter)

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
        self.inner = _lib.Incr_fn_filter_volatility_269144(ctx, )
        self.locals = FilterVolatilityLocals(self.inner)

    def next(self, minLength: Optional[int] = None, maxLength: Optional[int] = None, useVolatilityFilter: Optional[bool] = None) -> Optional[bool]:
        return self.inner.next(_23053_minLength=minLength, _23054_maxLength=maxLength, _23055_useVolatilityFilter=useVolatilityFilter)
    



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
    return _lib.Incr_fn_backtest_0e02ff(ctx=ctx, ).collect(_23059_high=high, _23060_low=low, _23061_open=open, _23062_startLongTrade=startLongTrade, _23063_endLongTrade=endLongTrade, _23064_startShortTrade=startShortTrade, _23065_endShortTrade=endShortTrade, _23066_isEarlySignalFlip=isEarlySignalFlip, _23067_maxBarsBackIndex=maxBarsBackIndex, _23068_thisBarIndex=thisBarIndex, _23069_src=src, _23070_useWorstCase=useWorstCase)

class BacktestLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def start_long_trade(self) -> float:
        return self.__inner._23072_start_long_trade()
  

    @property
    def start_short_trade(self) -> float:
        return self.__inner._23073_start_short_trade()
  

    @property
    def total_short_profit(self) -> float:
        return self.__inner._23074_total_short_profit()
  

    @property
    def total_long_profit(self) -> float:
        return self.__inner._23075_total_long_profit()
  

    @property
    def wins(self) -> int:
        return self.__inner._23076_wins()
  

    @property
    def losses(self) -> int:
        return self.__inner._23077_losses()
  

    @property
    def trade_count(self) -> int:
        return self.__inner._23078_trade_count()
  

    @property
    def early_signal_flip_count(self) -> int:
        return self.__inner._23079_early_signal_flip_count()
  

    @property
    def tookProfit(self) -> bool:
        return self.__inner._23080_tookProfit()
  
      

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
        self.inner = _lib.Incr_fn_backtest_0e02ff(ctx, )
        self.locals = BacktestLocals(self.inner)

    def next(self, high: float, low: float, open: float, startLongTrade: bool, endLongTrade: bool, startShortTrade: bool, endShortTrade: bool, isEarlySignalFlip: bool, maxBarsBackIndex: int, thisBarIndex: int, src: float, useWorstCase: bool) -> Optional[Tuple[float, float, float, float, str, float, float]]:
        return self.inner.next(_23059_high=high, _23060_low=low, _23061_open=open, _23062_startLongTrade=startLongTrade, _23063_endLongTrade=endLongTrade, _23064_startShortTrade=startShortTrade, _23065_endShortTrade=endShortTrade, _23066_isEarlySignalFlip=isEarlySignalFlip, _23067_maxBarsBackIndex=maxBarsBackIndex, _23068_thisBarIndex=thisBarIndex, _23069_src=src, _23070_useWorstCase=useWorstCase)
    


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
    return _lib.Incr_fn_main_f325ba(ctx=ctx, ).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_f325ba(ctx, )
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          