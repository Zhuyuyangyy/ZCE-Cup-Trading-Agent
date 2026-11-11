"""Conservative, next-bar futures research backtester. No broker connectivity."""
from dataclasses import dataclass
from typing import Sequence

@dataclass(frozen=True)
class Contract:
    symbol: str
    multiplier: float
    tick_size: float
    fee_per_side: float
    margin_rate: float
    slippage_ticks: int = 1

    def __post_init__(self):
        if not self.symbol or min(self.multiplier, self.tick_size, self.margin_rate) <= 0:
            raise ValueError('invalid contract parameters')
        if self.fee_per_side < 0 or self.slippage_ticks < 0 or self.margin_rate > 1:
            raise ValueError('invalid costs or margin')

@dataclass(frozen=True)
class Bar:
    timestamp: str
    open: float
    high: float
    low: float
    close: float

    def __post_init__(self):
        if min(self.open, self.high, self.low, self.close) <= 0 or self.high < max(self.open, self.close) or self.low > min(self.open, self.close):
            raise ValueError('invalid OHLC bar')

@dataclass(frozen=True)
class Trade:
    entry_time: str
    exit_time: str
    side: int
    entry: float
    exit: float
    pnl: float

@dataclass(frozen=True)
class Result:
    trades: tuple[Trade, ...]
    ending_equity: float
    max_drawdown_pct: float
    total_pnl: float


def backtest(bars: Sequence[Bar], signals: Sequence[int], contract: Contract,
             initial_equity: float = 500_000.0, max_margin_fraction: float = 0.1) -> Result:
    """Signals known at bar close; execute next open; 1 contract max.

    Signals: -1 short, 0 flat, +1 long. Position transitions close first,
    then reopen if margin permits. Mark-to-market equity tracks open PnL.
    No intrabar stop execution, overnight settlement or exchange limit rules.
    """
    if len(bars) != len(signals) or len(bars) < 2 or initial_equity <= 0 or not 0 < max_margin_fraction <= 1:
        raise ValueError('invalid backtest inputs')
    if any(s not in (-1, 0, 1) for s in signals):
        raise ValueError('signals must be -1, 0, +1')
    if len(set(b.timestamp for b in bars)) != len(bars) or any(bars[i].timestamp >= bars[i+1].timestamp for i in range(len(bars)-1)):
        raise ValueError('timestamps must be strictly increasing ISO-like strings')
    cash = initial_equity
    side, entry, entry_time = 0, 0.0, ''
    trades = []
    peak, max_dd = initial_equity, 0.0
    slip = contract.tick_size * contract.slippage_ticks

    def close_at(price: float, time: str):
        nonlocal cash, side
        fill = price - side * slip
        pnl = (fill - entry) * side * contract.multiplier - 2 * contract.fee_per_side
        cash += pnl
        trades.append(Trade(entry_time, time, side, entry, fill, pnl))
        side = 0

    for i in range(1, len(bars)):
        bar = bars[i]
        target = signals[i-1]
        if side and side != target:
            close_at(bar.open, bar.timestamp)
        if not side and target:
            fill = bar.open + target * slip
            required = fill * contract.multiplier * contract.margin_rate
            if required <= cash * max_margin_fraction:
                side, entry, entry_time = target, fill, bar.timestamp
        marked = cash + ((bar.close - entry) * side * contract.multiplier - 2 * contract.fee_per_side if side else 0)
        peak = max(peak, marked)
        max_dd = max(max_dd, (peak - marked) / peak * 100)
    if side:
        close_at(bars[-1].close, bars[-1].timestamp + ':final')
    peak = max(peak, cash)
    max_dd = max(max_dd, (peak - cash) / peak * 100)
    return Result(tuple(trades), cash, max_dd, cash - initial_equity)
