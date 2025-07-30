
  
from dataclasses import dataclass
from typing import Optional, Union, Literal, TypedDict, Any, Tuple, List
from datetime import datetime
from qpace import Ctx, Backtest
from qpace_content import _lib
  
  


def accdist(ctx: Ctx, ) -> List[float]:
    """
Total money flowing in and out (Accumulation/Distribution)

`accdist() -> float`
    """
    return _lib.Incr_fn_accdist_3ab84c(ctx=ctx, ).collect()

class AccdistLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Accdist:
    """
Total money flowing in and out (Accumulation/Distribution)

`accdist() -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_accdist_3ab84c(ctx, )
        self.locals = AccdistLocals(self.inner)

    def next(self, ) -> Optional[float]:
        return self.inner.next()
    



def cum(ctx: Ctx, src: List[float], ) -> List[float]:
    """
Adds up the values so far (running total)

`cum(series<float> src) -> float`
    """
    return _lib.Incr_fn_cum_5af557(ctx=ctx, ).collect(_19832_src=src)

class CumLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Cum:
    """
Adds up the values so far (running total)

`cum(series<float> src) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_cum_5af557(ctx, )
        self.locals = CumLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_19832_src=src)
    



def change(ctx: Ctx, src: List[float], ) -> List[float]:
    """
How much it moved from the previous bar

`change(series<float> src) -> series<float>`
    """
    return _lib.Incr_fn_change_a3512c(ctx=ctx, ).collect(_19834_src=src)

class ChangeLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Change:
    """
How much it moved from the previous bar

`change(series<float> src) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_change_a3512c(ctx, )
        self.locals = ChangeLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_19834_src=src)
    



def barssince(ctx: Ctx, condition: List[bool], ) -> List[int]:
    """
Number of bars since something happened

`barssince(series<bool> condition) -> int`
    """
    return _lib.Incr_fn_barssince_80d7e7(ctx=ctx, ).collect(_19836_condition=condition)

class BarssinceLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Barssince:
    """
Number of bars since something happened

`barssince(series<bool> condition) -> int`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_barssince_80d7e7(ctx, )
        self.locals = BarssinceLocals(self.inner)

    def next(self, condition: bool) -> Optional[int]:
        return self.inner.next(_19836_condition=condition)
    



def roc(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Speed of change over given bars

`roc(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_roc_ddd4be(ctx=ctx, ).collect(_19838_src=src, _19839_length=length)

class RocLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Roc:
    """
Speed of change over given bars

`roc(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_roc_ddd4be(ctx, )
        self.locals = RocLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19838_src=src, _19839_length=length)
    



def crossover(ctx: Ctx, source1: List[float], source2: List[float], ) -> List[bool]:
    """
When line1 moves above line2

`crossover(series<float> source1, series<float> source2) -> bool`
    """
    return _lib.Incr_fn_crossover_077290(ctx=ctx, ).collect(_19841_source1=source1, _19842_source2=source2)

class CrossoverLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Crossover:
    """
When line1 moves above line2

`crossover(series<float> source1, series<float> source2) -> bool`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_crossover_077290(ctx, )
        self.locals = CrossoverLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_19841_source1=source1, _19842_source2=source2)
    



def crossunder(ctx: Ctx, source1: List[float], source2: List[float], ) -> List[bool]:
    """
When line1 drops below line2

`crossunder(series<float> source1, series<float> source2) -> bool`
    """
    return _lib.Incr_fn_crossunder_4d7933(ctx=ctx, ).collect(_19844_source1=source1, _19845_source2=source2)

class CrossunderLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Crossunder:
    """
When line1 drops below line2

`crossunder(series<float> source1, series<float> source2) -> bool`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_crossunder_4d7933(ctx, )
        self.locals = CrossunderLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_19844_source1=source1, _19845_source2=source2)
    



def cross(ctx: Ctx, source1: List[float], source2: List[float], ) -> List[bool]:
    """
When two lines meet

`cross(series<float> source1, series<float> source2) -> bool`
    """
    return _lib.Incr_fn_cross_11f172(ctx=ctx, ).collect(_19847_source1=source1, _19848_source2=source2)

class CrossLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Cross:
    """
When two lines meet

`cross(series<float> source1, series<float> source2) -> bool`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_cross_11f172(ctx, )
        self.locals = CrossLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_19847_source1=source1, _19848_source2=source2)
    



def highestbars(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[int]:
    """
Bar index with highest value in period

`highestbars(series<float> src, int length = 14) -> int`
    """
    return _lib.Incr_fn_highestbars_26abee(ctx=ctx, ).collect(_19850_src=src, _19851_length=length)

class HighestbarsLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Highestbars:
    """
Bar index with highest value in period

`highestbars(series<float> src, int length = 14) -> int`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_highestbars_26abee(ctx, )
        self.locals = HighestbarsLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[int]:
        return self.inner.next(_19850_src=src, _19851_length=length)
    



def lowestbars(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[int]:
    """
Bar index with lowest value in period

`lowestbars(series<float> src, int length = 14) -> int`
    """
    return _lib.Incr_fn_lowestbars_2875db(ctx=ctx, ).collect(_19853_src=src, _19854_length=length)

class LowestbarsLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Lowestbars:
    """
Bar index with lowest value in period

`lowestbars(series<float> src, int length = 14) -> int`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_lowestbars_2875db(ctx, )
        self.locals = LowestbarsLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[int]:
        return self.inner.next(_19853_src=src, _19854_length=length)
    



def highest(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Highest value in period

`highest(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_highest_24d5b8(ctx=ctx, ).collect(_19856_src=src, _19857_length=length)

class HighestLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Highest:
    """
Highest value in period

`highest(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_highest_24d5b8(ctx, )
        self.locals = HighestLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19856_src=src, _19857_length=length)
    



def lowest(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Lowest value in period

`lowest(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_lowest_dc4efe(ctx=ctx, ).collect(_19859_src=src, _19860_length=length)

class LowestLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Lowest:
    """
Lowest value in period

`lowest(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_lowest_dc4efe(ctx, )
        self.locals = LowestLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19859_src=src, _19860_length=length)
    



def swma(ctx: Ctx, src: List[float], ) -> List[float]:
    """
Smoothed weighted moving average line

`swma(series<float> src) -> float`
    """
    return _lib.Incr_fn_swma_059946(ctx=ctx, ).collect(_19862_src=src)

class SwmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Swma:
    """
Smoothed weighted moving average line

`swma(series<float> src) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_swma_059946(ctx, )
        self.locals = SwmaLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_19862_src=src)
    



def sma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Simple moving average (plain average)

`sma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_sma_c20098(ctx=ctx, ).collect(_19864_src=src, _19865_length=length)

class SmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Sma:
    """
Simple moving average (plain average)

`sma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_sma_c20098(ctx, )
        self.locals = SmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19864_src=src, _19865_length=length)
    



def ema(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Exponential moving average (reacts faster)

`ema(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_ema_c91717(ctx=ctx, ).collect(_19867_src=src, _19868_length=length)

class EmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Ema:
    """
Exponential moving average (reacts faster)

`ema(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_ema_c91717(ctx, )
        self.locals = EmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19867_src=src, _19868_length=length)
    



def rma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
RMA used inside RSI

`rma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_rma_31c87c(ctx=ctx, ).collect(_19870_src=src, _19871_length=length)

class RmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Rma:
    """
RMA used inside RSI

`rma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_rma_31c87c(ctx, )
        self.locals = RmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19870_src=src, _19871_length=length)
    



def wma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Weighted moving average (recent bars matter more)

`wma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_wma_ce4e4c(ctx=ctx, ).collect(_19873_src=src, _19874_length=length)

class WmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Wma:
    """
Weighted moving average (recent bars matter more)

`wma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_wma_ce4e4c(ctx, )
        self.locals = WmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19873_src=src, _19874_length=length)
    



def lwma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Linear weighted moving average

`lwma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_lwma_188f3f(ctx=ctx, ).collect(_19876_src=src, _19877_length=length)

class LwmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Lwma:
    """
Linear weighted moving average

`lwma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_lwma_188f3f(ctx, )
        self.locals = LwmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19876_src=src, _19877_length=length)
    



def hma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Hull moving average (smooth and fast)

`hma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_hma_267161(ctx=ctx, ).collect(_19879_src=src, _19880_length=length)

class HmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Hma:
    """
Hull moving average (smooth and fast)

`hma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_hma_267161(ctx, )
        self.locals = HmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19879_src=src, _19880_length=length)
    



def vwma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Volume‑weighted moving average

`vwma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_vwma_29387c(ctx=ctx, ).collect(_19882_src=src, _19883_length=length)

class VwmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Vwma:
    """
Volume‑weighted moving average

`vwma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_vwma_29387c(ctx, )
        self.locals = VwmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19882_src=src, _19883_length=length)
    



def dev(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Standard deviation (how much it varies)

`dev(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_dev_37af23(ctx=ctx, ).collect(_19885_src=src, _19886_length=length)

class DevLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Dev:
    """
Standard deviation (how much it varies)

`dev(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_dev_37af23(ctx, )
        self.locals = DevLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19885_src=src, _19886_length=length)
    



def tr(ctx: Ctx, handle_na: Optional[bool] = None, ) -> List[float]:
    """
True range (how much price moved in bar)

`tr(bool handle_na = true) -> series<float>`
    """
    return _lib.Incr_fn_tr_4f203e(ctx=ctx, ).collect(_19888_handle_na=handle_na)

class TrLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Tr:
    """
True range (how much price moved in bar)

`tr(bool handle_na = true) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_tr_4f203e(ctx, )
        self.locals = TrLocals(self.inner)

    def next(self, handle_na: Optional[bool] = None) -> Optional[float]:
        return self.inner.next(_19888_handle_na=handle_na)
    



def atr(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Average true range (typical move size)

`atr(int length = 14) -> float`
    """
    return _lib.Incr_fn_atr_d19006(ctx=ctx, ).collect(_19890_length=length)

class AtrLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Atr:
    """
Average true range (typical move size)

`atr(int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_atr_d19006(ctx, )
        self.locals = AtrLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19890_length=length)
    



def rsi(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Relative Strength Index (momentum strength)

`rsi(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_rsi_7e833e(ctx=ctx, ).collect(_19892_src=src, _19893_length=length)

class RsiLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Rsi:
    """
Relative Strength Index (momentum strength)

`rsi(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_rsi_7e833e(ctx, )
        self.locals = RsiLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19892_src=src, _19893_length=length)
    



def cci(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Commodity Channel Index (price vs average)

`cci(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_cci_907245(ctx=ctx, ).collect(_19895_src=src, _19896_length=length)

class CciLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Cci:
    """
Commodity Channel Index (price vs average)

`cci(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_cci_907245(ctx, )
        self.locals = CciLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19895_src=src, _19896_length=length)
    



def stdev(ctx: Ctx, src: List[float], length: int, biased: Optional[bool] = None, ) -> List[float]:
    """
Standard deviation over period

`stdev(series<float> src, int length, bool biased = true) -> float`
    """
    return _lib.Incr_fn_stdev_19dd89(ctx=ctx, ).collect(_19898_src=src, _19899_length=length, _19900_biased=biased)

class StdevLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Stdev:
    """
Standard deviation over period

`stdev(series<float> src, int length, bool biased = true) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_stdev_19dd89(ctx, )
        self.locals = StdevLocals(self.inner)

    def next(self, src: float, length: int, biased: Optional[bool] = None) -> Optional[float]:
        return self.inner.next(_19898_src=src, _19899_length=length, _19900_biased=biased)
    



def aroon(ctx: Ctx, length: Optional[int] = None, ) -> Tuple[float, float]:
    """
Aroon indicator (time since highs/lows)

`aroon(int length = 14) -> [float, float]`
    """
    return _lib.Incr_fn_aroon_a7de64(ctx=ctx, ).collect(_19902_length=length)

class AroonLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Aroon:
    """
Aroon indicator (time since highs/lows)

`aroon(int length = 14) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_aroon_a7de64(ctx, )
        self.locals = AroonLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_19902_length=length)
    



def supertrend(ctx: Ctx, src: List[float], factor: float, atr_period: int, ) -> Tuple[float, int]:
    """
Supertrend line for direction

`supertrend(series<float> src, float factor, int atr_period) -> [float, int]`
    """
    return _lib.Incr_fn_supertrend_c8992d(ctx=ctx, ).collect(_19904_src=src, _19905_factor=factor, _19906_atr_period=atr_period)

class SupertrendLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Supertrend:
    """
Supertrend line for direction

`supertrend(series<float> src, float factor, int atr_period) -> [float, int]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_supertrend_c8992d(ctx, )
        self.locals = SupertrendLocals(self.inner)

    def next(self, src: float, factor: float, atr_period: int) -> Optional[Tuple[float, int]]:
        return self.inner.next(_19904_src=src, _19905_factor=factor, _19906_atr_period=atr_period)
    



def awesome_oscillator(ctx: Ctx, src: List[float], slow_length: Optional[int] = None, fast_length: Optional[int] = None, ) -> List[float]:
    """
Awesome Oscillator (momentum)

`awesome_oscillator(series<float> src, int slow_length = 5, int fast_length = 34) -> float`
    """
    return _lib.Incr_fn_awesome_oscillator_cd00ee(ctx=ctx, ).collect(_19908_src=src, _19909_slow_length=slow_length, _19910_fast_length=fast_length)

class AwesomeOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class AwesomeOscillator:
    """
Awesome Oscillator (momentum)

`awesome_oscillator(series<float> src, int slow_length = 5, int fast_length = 34) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_awesome_oscillator_cd00ee(ctx, )
        self.locals = AwesomeOscillatorLocals(self.inner)

    def next(self, src: float, slow_length: Optional[int] = None, fast_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19908_src=src, _19909_slow_length=slow_length, _19910_fast_length=fast_length)
    



def balance_of_power(ctx: Ctx, ) -> List[float]:
    """
Balance of power between buyers and sellers

`balance_of_power() -> float`
    """
    return _lib.Incr_fn_balance_of_power_f799b8(ctx=ctx, ).collect()

class BalanceOfPowerLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class BalanceOfPower:
    """
Balance of power between buyers and sellers

`balance_of_power() -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_balance_of_power_f799b8(ctx, )
        self.locals = BalanceOfPowerLocals(self.inner)

    def next(self, ) -> Optional[float]:
        return self.inner.next()
    



def bollinger_bands_pct_b(ctx: Ctx, src: List[float], length: Optional[int] = None, mult: Optional[float] = None, ) -> List[float]:
    """
%B – where price is inside Bollinger Bands (0‑1)

`bollinger_bands_pct_b(series<float> src, int length = 20, float mult = 2.0) -> float`
    """
    return _lib.Incr_fn_bollinger_bands_pct_b_e5a19f(ctx=ctx, ).collect(_19915_src=src, _19916_length=length, _19917_mult=mult)

class BollingerBandsPctBLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class BollingerBandsPctB:
    """
%B – where price is inside Bollinger Bands (0‑1)

`bollinger_bands_pct_b(series<float> src, int length = 20, float mult = 2.0) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_bollinger_bands_pct_b_e5a19f(ctx, )
        self.locals = BollingerBandsPctBLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None, mult: Optional[float] = None) -> Optional[float]:
        return self.inner.next(_19915_src=src, _19916_length=length, _19917_mult=mult)
    



def bollinger_bands_width(ctx: Ctx, src: List[float], length: Optional[int] = None, mult: Optional[float] = None, ) -> List[float]:
    """
Band width – how wide Bollinger Bands are

`bollinger_bands_width(series<float> src, int length = 20, float mult = 2.0) -> float`
    """
    return _lib.Incr_fn_bollinger_bands_width_929ca9(ctx=ctx, ).collect(_19924_src=src, _19925_length=length, _19926_mult=mult)

class BollingerBandsWidthLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class BollingerBandsWidth:
    """
Band width – how wide Bollinger Bands are

`bollinger_bands_width(series<float> src, int length = 20, float mult = 2.0) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_bollinger_bands_width_929ca9(ctx, )
        self.locals = BollingerBandsWidthLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None, mult: Optional[float] = None) -> Optional[float]:
        return self.inner.next(_19924_src=src, _19925_length=length, _19926_mult=mult)
    



def bollinger_bands(ctx: Ctx, src: List[float], length: Optional[int] = None, mult: Optional[float] = None, ) -> Tuple[float, float]:
    """
Gives upper and lower Bollinger Bands

`bollinger_bands(series<float> src, int length = 20, float mult = 2.0) -> [float, float]`
    """
    return _lib.Incr_fn_bollinger_bands_5ee2cc(ctx=ctx, ).collect(_19933_src=src, _19934_length=length, _19935_mult=mult)

class BollingerBandsLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class BollingerBands:
    """
Gives upper and lower Bollinger Bands

`bollinger_bands(series<float> src, int length = 20, float mult = 2.0) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_bollinger_bands_5ee2cc(ctx, )
        self.locals = BollingerBandsLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None, mult: Optional[float] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_19933_src=src, _19934_length=length, _19935_mult=mult)
    



def chaikin_money_flow(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Chaikin Money Flow – volume weighted flow

`chaikin_money_flow(int length = 20) -> float`
    """
    return _lib.Incr_fn_chaikin_money_flow_0ca352(ctx=ctx, ).collect(_19941_length=length)

class ChaikinMoneyFlowLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def cumVol(self) -> float:
        return self.__inner._19942_cumVol()
  
      

class ChaikinMoneyFlow:
    """
Chaikin Money Flow – volume weighted flow

`chaikin_money_flow(int length = 20) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_chaikin_money_flow_0ca352(ctx, )
        self.locals = ChaikinMoneyFlowLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19941_length=length)
    



def chande_kroll_stop(ctx: Ctx, atr_length: Optional[int] = None, atr_coeff: Optional[float] = None, stop_length: Optional[int] = None, ) -> Tuple[float, float]:
    """
Chande‑Kroll stop lines

`chande_kroll_stop(int atr_length = 10, float atr_coeff = 1.0, int stop_length = 9) -> [float, float]`
    """
    return _lib.Incr_fn_chande_kroll_stop_6e0fe8(ctx=ctx, ).collect(_19946_atr_length=atr_length, _19947_atr_coeff=atr_coeff, _19948_stop_length=stop_length)

class ChandeKrollStopLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class ChandeKrollStop:
    """
Chande‑Kroll stop lines

`chande_kroll_stop(int atr_length = 10, float atr_coeff = 1.0, int stop_length = 9) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_chande_kroll_stop_6e0fe8(ctx, )
        self.locals = ChandeKrollStopLocals(self.inner)

    def next(self, atr_length: Optional[int] = None, atr_coeff: Optional[float] = None, stop_length: Optional[int] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_19946_atr_length=atr_length, _19947_atr_coeff=atr_coeff, _19948_stop_length=stop_length)
    



def choppiness_index(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Choppiness Index – tells if market is sideways or trending

`choppiness_index(int length = 14) -> float`
    """
    return _lib.Incr_fn_choppiness_index_1c8243(ctx=ctx, ).collect(_19957_length=length)

class ChoppinessIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class ChoppinessIndex:
    """
Choppiness Index – tells if market is sideways or trending

`choppiness_index(int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_choppiness_index_1c8243(ctx, )
        self.locals = ChoppinessIndexLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19957_length=length)
    



def connors_rsi(ctx: Ctx, src: List[float], rsi_length: Optional[int] = None, up_down_length: Optional[int] = None, roc_length: Optional[int] = None, ) -> List[float]:
    """
`connors_rsi(series<float> src, int rsi_length = 3, int up_down_length = 2, int roc_length = 100) -> float`
    """
    return _lib.Incr_fn_connors_rsi_d362f7(ctx=ctx, ).collect(_19964_src=src, _19965_rsi_length=rsi_length, _19966_up_down_length=up_down_length, _19967_roc_length=roc_length)

class ConnorsRsiLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class ConnorsRsi:
    """
`connors_rsi(series<float> src, int rsi_length = 3, int up_down_length = 2, int roc_length = 100) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_connors_rsi_d362f7(ctx, )
        self.locals = ConnorsRsiLocals(self.inner)

    def next(self, src: float, rsi_length: Optional[int] = None, up_down_length: Optional[int] = None, roc_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19964_src=src, _19965_rsi_length=rsi_length, _19966_up_down_length=up_down_length, _19967_roc_length=roc_length)
    



def coppock_curve(ctx: Ctx, src: List[float], wma_length: Optional[int] = None, long_roc_length: Optional[int] = None, short_roc_length: Optional[int] = None, ) -> List[float]:
    """
Coppock Curve – long‑term momentum

`coppock_curve(series<float> src, int wma_length = 10, int long_roc_length = 14, int short_roc_length = 11) -> float`
    """
    return _lib.Incr_fn_coppock_curve_cf3cad(ctx=ctx, ).collect(_19973_src=src, _19974_wma_length=wma_length, _19975_long_roc_length=long_roc_length, _19976_short_roc_length=short_roc_length)

class CoppockCurveLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class CoppockCurve:
    """
Coppock Curve – long‑term momentum

`coppock_curve(series<float> src, int wma_length = 10, int long_roc_length = 14, int short_roc_length = 11) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_coppock_curve_cf3cad(ctx, )
        self.locals = CoppockCurveLocals(self.inner)

    def next(self, src: float, wma_length: Optional[int] = None, long_roc_length: Optional[int] = None, short_roc_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19973_src=src, _19974_wma_length=wma_length, _19975_long_roc_length=long_roc_length, _19976_short_roc_length=short_roc_length)
    



def donchian_channel(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> Tuple[float, float, float]:
    """
Donchian Channel highs/lows

`donchian_channel(series<float> src, int length = 20) -> [float, float, float]`
    """
    return _lib.Incr_fn_donchian_channel_226ba3(ctx=ctx, ).collect(_19978_src=src, _19979_length=length)

class DonchianChannelLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class DonchianChannel:
    """
Donchian Channel highs/lows

`donchian_channel(series<float> src, int length = 20) -> [float, float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_donchian_channel_226ba3(ctx, )
        self.locals = DonchianChannelLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[Tuple[float, float, float]]:
        return self.inner.next(_19978_src=src, _19979_length=length)
    



def macd(ctx: Ctx, src: List[float], short_length: Optional[int] = None, long_length: Optional[int] = None, ) -> List[float]:
    """
MACD line (fast trend vs slow)

`macd(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """
    return _lib.Incr_fn_macd_d63a4c(ctx=ctx, ).collect(_19984_src=src, _19985_short_length=short_length, _19986_long_length=long_length)

class MacdLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Macd:
    """
MACD line (fast trend vs slow)

`macd(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_macd_d63a4c(ctx, )
        self.locals = MacdLocals(self.inner)

    def next(self, src: float, short_length: Optional[int] = None, long_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19984_src=src, _19985_short_length=short_length, _19986_long_length=long_length)
    



def price_oscillator(ctx: Ctx, src: List[float], short_length: Optional[int] = None, long_length: Optional[int] = None, ) -> List[float]:
    """
Price oscillator in percent

`price_oscillator(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """
    return _lib.Incr_fn_price_oscillator_8bcba9(ctx=ctx, ).collect(_19989_src=src, _19990_short_length=short_length, _19991_long_length=long_length)

class PriceOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class PriceOscillator:
    """
Price oscillator in percent

`price_oscillator(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_price_oscillator_8bcba9(ctx, )
        self.locals = PriceOscillatorLocals(self.inner)

    def next(self, src: float, short_length: Optional[int] = None, long_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19989_src=src, _19990_short_length=short_length, _19991_long_length=long_length)
    



def relative_vigor_index(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Relative Vigor Index – strength of close vs range

`relative_vigor_index(int length = 14) -> float`
    """
    return _lib.Incr_fn_relative_vigor_index_ed6811(ctx=ctx, ).collect(_19996_length=length)

class RelativeVigorIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class RelativeVigorIndex:
    """
Relative Vigor Index – strength of close vs range

`relative_vigor_index(int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_relative_vigor_index_ed6811(ctx, )
        self.locals = RelativeVigorIndexLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19996_length=length)
    



def relative_volatility_index(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Relative Volatility Index – like RSI but for volatility

`relative_volatility_index(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_relative_volatility_index_e9853a(ctx=ctx, ).collect(_19998_src=src, _19999_length=length)

class RelativeVolatilityIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class RelativeVolatilityIndex:
    """
Relative Volatility Index – like RSI but for volatility

`relative_volatility_index(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_relative_volatility_index_e9853a(ctx, )
        self.locals = RelativeVolatilityIndexLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_19998_src=src, _19999_length=length)
    



def stochastic_rsi(ctx: Ctx, src: List[float], stoch_length: Optional[int] = None, rsi_length: Optional[int] = None, k: Optional[int] = None, d: Optional[int] = None, ) -> Tuple[float, float]:
    """
Stochastic RSI

`stochastic_rsi(series<float> src, int stoch_length = 14, int rsi_length = 14, int k = 3, int d = 3) -> [float, float]`
    """
    return _lib.Incr_fn_stochastic_rsi_5e52d4(ctx=ctx, ).collect(_20005_src=src, _20006_stoch_length=stoch_length, _20007_rsi_length=rsi_length, _20008_k=k, _20009_d=d)

class StochasticRsiLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class StochasticRsi:
    """
Stochastic RSI

`stochastic_rsi(series<float> src, int stoch_length = 14, int rsi_length = 14, int k = 3, int d = 3) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_stochastic_rsi_5e52d4(ctx, )
        self.locals = StochasticRsiLocals(self.inner)

    def next(self, src: float, stoch_length: Optional[int] = None, rsi_length: Optional[int] = None, k: Optional[int] = None, d: Optional[int] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_20005_src=src, _20006_stoch_length=stoch_length, _20007_rsi_length=rsi_length, _20008_k=k, _20009_d=d)
    



def ultimate_oscillator(ctx: Ctx, fast_length: Optional[int] = None, medium_length: Optional[int] = None, slow_length: Optional[int] = None, ) -> List[float]:
    """
Ultimate Oscillator – combines 3 speeds

`ultimate_oscillator(int fast_length = 7, int medium_length = 14, int slow_length = 28) -> float`
    """
    return _lib.Incr_fn_ultimate_oscillator_a07920(ctx=ctx, ).collect(_20018_fast_length=fast_length, _20019_medium_length=medium_length, _20020_slow_length=slow_length)

class UltimateOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class UltimateOscillator:
    """
Ultimate Oscillator – combines 3 speeds

`ultimate_oscillator(int fast_length = 7, int medium_length = 14, int slow_length = 28) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_ultimate_oscillator_a07920(ctx, )
        self.locals = UltimateOscillatorLocals(self.inner)

    def next(self, fast_length: Optional[int] = None, medium_length: Optional[int] = None, slow_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_20018_fast_length=fast_length, _20019_medium_length=medium_length, _20020_slow_length=slow_length)
    



def volume_oscillator(ctx: Ctx, short_length: Optional[int] = None, long_length: Optional[int] = None, ) -> List[float]:
    """
Volume Oscillator – volume momentum

`volume_oscillator(int short_length = 5, int long_length = 10) -> float`
    """
    return _lib.Incr_fn_volume_oscillator_d12969(ctx=ctx, ).collect(_20030_short_length=short_length, _20031_long_length=long_length)

class VolumeOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class VolumeOscillator:
    """
Volume Oscillator – volume momentum

`volume_oscillator(int short_length = 5, int long_length = 10) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_volume_oscillator_d12969(ctx, )
        self.locals = VolumeOscillatorLocals(self.inner)

    def next(self, short_length: Optional[int] = None, long_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_20030_short_length=short_length, _20031_long_length=long_length)
    



def vortex_indicator(ctx: Ctx, length: Optional[int] = None, ) -> Tuple[float, float]:
    """
Vortex Indicator – shows trend direction

`vortex_indicator(int length = 14) -> [float, float]`
    """
    return _lib.Incr_fn_vortex_indicator_b27bd7(ctx=ctx, ).collect(_20036_length=length)

class VortexIndicatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class VortexIndicator:
    """
Vortex Indicator – shows trend direction

`vortex_indicator(int length = 14) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_vortex_indicator_b27bd7(ctx, )
        self.locals = VortexIndicatorLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_20036_length=length)
    



def williams_pct_r(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Williams %R – overbought/oversold

`williams_pct_r(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_williams_pct_r_4d1333(ctx=ctx, ).collect(_20043_src=src, _20044_length=length)

class WilliamsPctRLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class WilliamsPctR:
    """
Williams %R – overbought/oversold

`williams_pct_r(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_williams_pct_r_4d1333(ctx, )
        self.locals = WilliamsPctRLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_20043_src=src, _20044_length=length)
    



def advance_decline_ratio(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Advance/Decline Ratio (Bars)

`advance_decline_ratio(int length = 9) -> float`
    """
    return _lib.Incr_fn_advance_decline_ratio_426263(ctx=ctx, ).collect(_20049_length=length)

class AdvanceDeclineRatioLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class AdvanceDeclineRatio:
    """
Advance/Decline Ratio (Bars)

`advance_decline_ratio(int length = 9) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_advance_decline_ratio_426263(ctx, )
        self.locals = AdvanceDeclineRatioLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_20049_length=length)
    



def detrended_price_oscillator(ctx: Ctx, length: Optional[int] = None, centered: Optional[bool] = None, ) -> List[float]:
    """
Detrended Price Oscillator (DPO)

`detrended_price_oscillator(int length = 21, bool centered = false) -> series<float>`
    """
    return _lib.Incr_fn_detrended_price_oscillator_233738(ctx=ctx, ).collect(_20055_length=length, _20056_centered=centered)

class DetrendedPriceOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class DetrendedPriceOscillator:
    """
Detrended Price Oscillator (DPO)

`detrended_price_oscillator(int length = 21, bool centered = false) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_detrended_price_oscillator_233738(ctx, )
        self.locals = DetrendedPriceOscillatorLocals(self.inner)

    def next(self, length: Optional[int] = None, centered: Optional[bool] = None) -> Optional[float]:
        return self.inner.next(_20055_length=length, _20056_centered=centered)
    



def bull_bear_power(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Bull Bear Power (BBP)

`bull_bear_power(int length = 13) -> series<float>`
    """
    return _lib.Incr_fn_bull_bear_power_8468cc(ctx=ctx, ).collect(_20061_length=length)

class BullBearPowerLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class BullBearPower:
    """
Bull Bear Power (BBP)

`bull_bear_power(int length = 13) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_bull_bear_power_8468cc(ctx, )
        self.locals = BullBearPowerLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_20061_length=length)
    



def absolute_price_oscillator(ctx: Ctx, src: List[float], fast_length: Optional[int] = None, slow_length: Optional[int] = None, ) -> List[float]:
    """
Absolute Price Oscillator (APO)

`absolute_price_oscillator(series<float> src, int fast_length = 12, int slow_length = 26) -> float`
    """
    return _lib.Incr_fn_absolute_price_oscillator_77c4a5(ctx=ctx, ).collect(_20067_src=src, _20068_fast_length=fast_length, _20069_slow_length=slow_length)

class AbsolutePriceOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class AbsolutePriceOscillator:
    """
Absolute Price Oscillator (APO)

`absolute_price_oscillator(series<float> src, int fast_length = 12, int slow_length = 26) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_absolute_price_oscillator_77c4a5(ctx, )
        self.locals = AbsolutePriceOscillatorLocals(self.inner)

    def next(self, src: float, fast_length: Optional[int] = None, slow_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_20067_src=src, _20068_fast_length=fast_length, _20069_slow_length=slow_length)
    



def know_sure_thing(ctx: Ctx, src: List[float], roc_length1: Optional[int] = None, roc_length2: Optional[int] = None, roc_length3: Optional[int] = None, roc_length4: Optional[int] = None, sma_length1: Optional[int] = None, sma_length2: Optional[int] = None, sma_length3: Optional[int] = None, sma_length4: Optional[int] = None, sig_length: Optional[int] = None, ) -> Tuple[float, float]:
    """
Know Sure Thing (KST)

`know_sure_thing(series<float> src, int roc_length1 = 10, int roc_length2 = 15, int roc_length3 = 20, int roc_length4 = 30, int sma_length1 = 10, int sma_length2 = 10, int sma_length3 = 10, int sma_length4 = 15, int sig_length = 9) -> [float, float]`
    """
    return _lib.Incr_fn_know_sure_thing_386599(ctx=ctx, ).collect(_20073_src=src, _20074_roc_length1=roc_length1, _20075_roc_length2=roc_length2, _20076_roc_length3=roc_length3, _20077_roc_length4=roc_length4, _20078_sma_length1=sma_length1, _20079_sma_length2=sma_length2, _20080_sma_length3=sma_length3, _20081_sma_length4=sma_length4, _20082_sig_length=sig_length)

class KnowSureThingLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class KnowSureThing:
    """
Know Sure Thing (KST)

`know_sure_thing(series<float> src, int roc_length1 = 10, int roc_length2 = 15, int roc_length3 = 20, int roc_length4 = 30, int sma_length1 = 10, int sma_length2 = 10, int sma_length3 = 10, int sma_length4 = 15, int sig_length = 9) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_know_sure_thing_386599(ctx, )
        self.locals = KnowSureThingLocals(self.inner)

    def next(self, src: float, roc_length1: Optional[int] = None, roc_length2: Optional[int] = None, roc_length3: Optional[int] = None, roc_length4: Optional[int] = None, sma_length1: Optional[int] = None, sma_length2: Optional[int] = None, sma_length3: Optional[int] = None, sma_length4: Optional[int] = None, sig_length: Optional[int] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_20073_src=src, _20074_roc_length1=roc_length1, _20075_roc_length2=roc_length2, _20076_roc_length3=roc_length3, _20077_roc_length4=roc_length4, _20078_sma_length1=sma_length1, _20079_sma_length2=sma_length2, _20080_sma_length3=sma_length3, _20081_sma_length4=sma_length4, _20082_sig_length=sig_length)
    



def momentum(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Momentum (MOM)

`momentum(series<float> src, int length = 10) -> series<float>`
    """
    return _lib.Incr_fn_momentum_4e1198(ctx=ctx, ).collect(_20090_src=src, _20091_length=length)

class MomentumLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Momentum:
    """
Momentum (MOM)

`momentum(series<float> src, int length = 10) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_momentum_4e1198(ctx, )
        self.locals = MomentumLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_20090_src=src, _20091_length=length)
    



def trix(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Trix

`trix(series<float> src, int length = 18) -> series<float>`
    """
    return _lib.Incr_fn_trix_25fb5a(ctx=ctx, ).collect(_20093_src=src, _20094_length=length)

class TrixLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Trix:
    """
Trix

`trix(series<float> src, int length = 18) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_trix_25fb5a(ctx, )
        self.locals = TrixLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_20093_src=src, _20094_length=length)
    



def true_strength_index(ctx: Ctx, src: List[float], long_length: Optional[int] = None, short_length: Optional[int] = None, ) -> List[float]:
    """
True Strength Index (TSI)

`true_strength_index(series<float> src, int long_length = 25, int short_length = 13) -> float`
    """
    return _lib.Incr_fn_true_strength_index_a98bad(ctx=ctx, ).collect(_20096_src=src, _20097_long_length=long_length, _20098_short_length=short_length)

class TrueStrengthIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class TrueStrengthIndex:
    """
True Strength Index (TSI)

`true_strength_index(series<float> src, int long_length = 25, int short_length = 13) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_true_strength_index_a98bad(ctx, )
        self.locals = TrueStrengthIndexLocals(self.inner)

    def next(self, src: float, long_length: Optional[int] = None, short_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_20096_src=src, _20097_long_length=long_length, _20098_short_length=short_length)
    



def dema(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Double Exponential Moving Average (DEMA)

`dema(series<float> src, int length = 9) -> float`
    """
    return _lib.Incr_fn_dema_82aea8(ctx=ctx, ).collect(_20104_src=src, _20105_length=length)

class DemaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Dema:
    """
Double Exponential Moving Average (DEMA)

`dema(series<float> src, int length = 9) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_dema_82aea8(ctx, )
        self.locals = DemaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_20104_src=src, _20105_length=length)
    



def fwma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Fibonacci Weighted Moving Average (FWMA)

`fwma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_fwma_51127e(ctx=ctx, ).collect(_20114_src=src, _20115_length=length)

class FwmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Fwma:
    """
Fibonacci Weighted Moving Average (FWMA)

`fwma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_fwma_51127e(ctx, )
        self.locals = FwmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_20114_src=src, _20115_length=length)
    



def money_flow_index(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Money Flow Index (MFI)

`money_flow_index(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_money_flow_index_27a924(ctx=ctx, ).collect(_20121_src=src, _20122_length=length)

class MoneyFlowIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class MoneyFlowIndex:
    """
Money Flow Index (MFI)

`money_flow_index(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_money_flow_index_27a924(ctx, )
        self.locals = MoneyFlowIndexLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_20121_src=src, _20122_length=length)
    



def ease_of_movement(ctx: Ctx, length: Optional[int] = None, divisor: Optional[int] = None, ) -> List[float]:
    """
Ease of Movement (EOM)

`ease_of_movement(int length = 14, int divisor = 10000) -> float`
    """
    return _lib.Incr_fn_ease_of_movement_0d2a09(ctx=ctx, ).collect(_20124_length=length, _20125_divisor=divisor)

class EaseOfMovementLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class EaseOfMovement:
    """
Ease of Movement (EOM)

`ease_of_movement(int length = 14, int divisor = 10000) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_ease_of_movement_0d2a09(ctx, )
        self.locals = EaseOfMovementLocals(self.inner)

    def next(self, length: Optional[int] = None, divisor: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_20124_length=length, _20125_divisor=divisor)
    



def elder_force_index(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Elder Force Index (EFI)

`elder_force_index(int length = 13) -> float`
    """
    return _lib.Incr_fn_elder_force_index_f06f02(ctx=ctx, ).collect(_20127_length=length)

class ElderForceIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class ElderForceIndex:
    """
Elder Force Index (EFI)

`elder_force_index(int length = 13) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_elder_force_index_f06f02(ctx, )
        self.locals = ElderForceIndexLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_20127_length=length)
    



def tema(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Tripple Exponential Moving Average (TEMA)

`tema(series<float> src, int length = 9) -> float`
    """
    return _lib.Incr_fn_tema_c0ad54(ctx=ctx, ).collect(_20129_src=src, _20130_length=length)

class TemaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Tema:
    """
Tripple Exponential Moving Average (TEMA)

`tema(series<float> src, int length = 9) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_tema_c0ad54(ctx, )
        self.locals = TemaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_20129_src=src, _20130_length=length)
    


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
    return _lib.Incr_fn_main_c487ef(ctx=ctx, ).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_c487ef(ctx, )
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          