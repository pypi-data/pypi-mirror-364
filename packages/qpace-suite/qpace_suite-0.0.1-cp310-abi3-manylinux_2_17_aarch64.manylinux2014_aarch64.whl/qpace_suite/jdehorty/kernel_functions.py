
  
from dataclasses import dataclass
from typing import Optional, Union, Literal, TypedDict, Any, Tuple, List
from datetime import datetime
from qpace import Ctx, Backtest
from qpace_suite import _lib
  
  


def rational_quadratic(ctx: Ctx, _src: List[float], _lookback: int, _relativeWeight: float, startAtBar: int, ) -> List[float]:
    """
@function Rational Quadratic Kernel - An infinite sum of Gaussian Kernels of different length scales.
 @param _src <float series> The source series.
 @param _lookback <simple int> The number of bars used for the estimation. This is a sliding value that represents the most recent historical bars.
 @param _relativeWeight <simple float> Relative weighting of time frames. Smaller values resut in a more stretched out curve and larger values will result in a more wiggly curve. As this value approaches zero, the longer time frames will exert more influence on the estimation. As this value approaches infinity, the behavior of the Rational Quadratic Kernel will become identical to the Gaussian kernel.
 @param _startAtBar <simple int> Bar index on which to start regression. The first bars of a chart are often highly volatile, and omission of these initial bars often leads to a better overall fit.
 @returns yhat <float series> The estimated values according to the Rational Quadratic Kernel.

`rationalQuadratic(series<float> _src, int _lookback, float _relativeWeight, int startAtBar) -> float`
    """
    return _lib.Incr_fn_rationalQuadratic_440b03(ctx=ctx, ).collect(_31643__src=_src, _31644__lookback=_lookback, _31645__relativeWeight=_relativeWeight, _31646_startAtBar=startAtBar)

class RationalQuadraticLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class RationalQuadratic:
    """
@function Rational Quadratic Kernel - An infinite sum of Gaussian Kernels of different length scales.
 @param _src <float series> The source series.
 @param _lookback <simple int> The number of bars used for the estimation. This is a sliding value that represents the most recent historical bars.
 @param _relativeWeight <simple float> Relative weighting of time frames. Smaller values resut in a more stretched out curve and larger values will result in a more wiggly curve. As this value approaches zero, the longer time frames will exert more influence on the estimation. As this value approaches infinity, the behavior of the Rational Quadratic Kernel will become identical to the Gaussian kernel.
 @param _startAtBar <simple int> Bar index on which to start regression. The first bars of a chart are often highly volatile, and omission of these initial bars often leads to a better overall fit.
 @returns yhat <float series> The estimated values according to the Rational Quadratic Kernel.

`rationalQuadratic(series<float> _src, int _lookback, float _relativeWeight, int startAtBar) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_rationalQuadratic_440b03(ctx, )
        self.locals = RationalQuadraticLocals(self.inner)

    def next(self, _src: float, _lookback: int, _relativeWeight: float, startAtBar: int) -> Optional[float]:
        return self.inner.next(_31643__src=_src, _31644__lookback=_lookback, _31645__relativeWeight=_relativeWeight, _31646_startAtBar=startAtBar)
    



def gaussian(ctx: Ctx, _src: List[float], _lookback: int, startAtBar: int, ) -> List[float]:
    """
@function Gaussian Kernel - A weighted average of the source series. The weights are determined by the Radial Basis Function (RBF).
 @param _src <float series> The source series.
 @param _lookback <simple int> The number of bars used for the estimation. This is a sliding value that represents the most recent historical bars.
 @param _startAtBar <simple int> Bar index on which to start regression. The first bars of a chart are often highly volatile, and omission of these initial bars often leads to a better overall fit.
 @returns yhat <float series> The estimated values according to the Gaussian Kernel.

`gaussian(series<float> _src, int _lookback, int startAtBar) -> float`
    """
    return _lib.Incr_fn_gaussian_cafeea(ctx=ctx, ).collect(_31655__src=_src, _31656__lookback=_lookback, _31657_startAtBar=startAtBar)

class GaussianLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Gaussian:
    """
@function Gaussian Kernel - A weighted average of the source series. The weights are determined by the Radial Basis Function (RBF).
 @param _src <float series> The source series.
 @param _lookback <simple int> The number of bars used for the estimation. This is a sliding value that represents the most recent historical bars.
 @param _startAtBar <simple int> Bar index on which to start regression. The first bars of a chart are often highly volatile, and omission of these initial bars often leads to a better overall fit.
 @returns yhat <float series> The estimated values according to the Gaussian Kernel.

`gaussian(series<float> _src, int _lookback, int startAtBar) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_gaussian_cafeea(ctx, )
        self.locals = GaussianLocals(self.inner)

    def next(self, _src: float, _lookback: int, startAtBar: int) -> Optional[float]:
        return self.inner.next(_31655__src=_src, _31656__lookback=_lookback, _31657_startAtBar=startAtBar)
    



def periodic(ctx: Ctx, _src: List[float], _lookback: int, _period: int, startAtBar: int, ) -> List[float]:
    """
@function Periodic Kernel - The periodic kernel (derived by David Mackay) allows one to model functions which repeat themselves exactly.
 @param _src <float series> The source series.
 @param _lookback <simple int> The number of bars used for the estimation. This is a sliding value that represents the most recent historical bars.
 @param _period <simple int> The distance between repititions of the function.
 @param _startAtBar <simple int> Bar index on which to start regression. The first bars of a chart are often highly volatile, and omission of these initial bars often leads to a better overall fit.
 @returns yhat <float series> The estimated values according to the Periodic Kernel.

`periodic(series<float> _src, int _lookback, int _period, int startAtBar) -> float`
    """
    return _lib.Incr_fn_periodic_26c76e(ctx=ctx, ).collect(_31666__src=_src, _31667__lookback=_lookback, _31668__period=_period, _31669_startAtBar=startAtBar)

class PeriodicLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Periodic:
    """
@function Periodic Kernel - The periodic kernel (derived by David Mackay) allows one to model functions which repeat themselves exactly.
 @param _src <float series> The source series.
 @param _lookback <simple int> The number of bars used for the estimation. This is a sliding value that represents the most recent historical bars.
 @param _period <simple int> The distance between repititions of the function.
 @param _startAtBar <simple int> Bar index on which to start regression. The first bars of a chart are often highly volatile, and omission of these initial bars often leads to a better overall fit.
 @returns yhat <float series> The estimated values according to the Periodic Kernel.

`periodic(series<float> _src, int _lookback, int _period, int startAtBar) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_periodic_26c76e(ctx, )
        self.locals = PeriodicLocals(self.inner)

    def next(self, _src: float, _lookback: int, _period: int, startAtBar: int) -> Optional[float]:
        return self.inner.next(_31666__src=_src, _31667__lookback=_lookback, _31668__period=_period, _31669_startAtBar=startAtBar)
    



def locally_periodic(ctx: Ctx, _src: List[float], _lookback: int, _period: int, startAtBar: int, ) -> List[float]:
    """
@function Locally Periodic Kernel - The locally periodic kernel is a periodic function that slowly varies with time. It is the product of the Periodic Kernel and the Gaussian Kernel.
 @param _src <float series> The source series.
 @param _lookback <simple int> The number of bars used for the estimation. This is a sliding value that represents the most recent historical bars.
 @param _period <simple int> The distance between repititions of the function.
 @param _startAtBar <simple int> Bar index on which to start regression. The first bars of a chart are often highly volatile, and omission of these initial bars often leads to a better overall fit.
 @returns yhat <float series> The estimated values according to the Locally Periodic Kernel.

`locallyPeriodic(series<float> _src, int _lookback, int _period, int startAtBar) -> float`
    """
    return _lib.Incr_fn_locallyPeriodic_40ec44(ctx=ctx, ).collect(_31678__src=_src, _31679__lookback=_lookback, _31680__period=_period, _31681_startAtBar=startAtBar)

class LocallyPeriodicLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class LocallyPeriodic:
    """
@function Locally Periodic Kernel - The locally periodic kernel is a periodic function that slowly varies with time. It is the product of the Periodic Kernel and the Gaussian Kernel.
 @param _src <float series> The source series.
 @param _lookback <simple int> The number of bars used for the estimation. This is a sliding value that represents the most recent historical bars.
 @param _period <simple int> The distance between repititions of the function.
 @param _startAtBar <simple int> Bar index on which to start regression. The first bars of a chart are often highly volatile, and omission of these initial bars often leads to a better overall fit.
 @returns yhat <float series> The estimated values according to the Locally Periodic Kernel.

`locallyPeriodic(series<float> _src, int _lookback, int _period, int startAtBar) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_locallyPeriodic_40ec44(ctx, )
        self.locals = LocallyPeriodicLocals(self.inner)

    def next(self, _src: float, _lookback: int, _period: int, startAtBar: int) -> Optional[float]:
        return self.inner.next(_31678__src=_src, _31679__lookback=_lookback, _31680__period=_period, _31681_startAtBar=startAtBar)
    


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
    return _lib.Incr_fn_main_f83782(ctx=ctx, ).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_f83782(ctx, )
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          