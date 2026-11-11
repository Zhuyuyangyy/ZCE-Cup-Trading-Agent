# ZCE-Cup-Trading-Agent

Offline research prototype for commodity-futures **simulated** trading competitions.
No broker connection, order execution, mobile automation, or live trading.

## Scope (P1)
- Generic futures contract configuration (multiplier, tick, per-side fees, margin, slippage).
- CSV OHLC reader (`timestamp,open,high,low,close`), strictly increasing timestamps.
- Long/short/flat bar-close signals, **next-bar open** fills, one contract maximum.
- Conservative adverse slippage, fees, margin-based entry guard, mark-to-market drawdown.
- Standard-library-only unit tests.

## Run
```bash
python -m unittest discover -s tests -v
```

## Known limitations / safety
This is a research skeleton, **not a competition-ready simulator**. Exchange contract specs, commission schedules, daily settlement, trading sessions, price limits, delivery restrictions, stop execution, contract rolls, liquidity, partial fills and risk-of-ruin models are NOT implemented. No claim of positive expected returns. Do not enable automated execution. Verify competition rules before any UI automation. Never assume contract parameters are current; the `DEMO` test contract is fictitious.

## Provenance
Inspired by reusable falsification concepts from `Zhuyuyangyy/PaperTrade-Agent-V2` (path-aware replay, explicit friction, out-of-sample controls). No source code copied. Next milestone: real historical dataset adapter and reproducible walk-forward/random baselines.
