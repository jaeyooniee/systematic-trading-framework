"""
Systematic Trading Framework — main runner

Usage:
    python main.py

Runs three demos in order:
    1. Moving Average Crossover parameter sweep  (NVDA 2020-2024)
    2. Pairs Trading backtest                    (KO vs PEP 2015-2024)
    3. Walk-forward validation                   (MA crossover on NVDA 2010-2023)
"""

import pandas as pd

from systematic_trading.data.data_loader import DataLoader
from systematic_trading.engine.engine import Engine
from systematic_trading.engine.pairs_engine import PairsEngine
from systematic_trading.engine.portfolio import Portfolio
from systematic_trading.strategies.moving_average import MovingAverageCrossover
from systematic_trading.strategies.rsi_mean_reversion import RSIMeanReversion
from systematic_trading.strategies.pairs_trading import PairsTrading
from systematic_trading.analysis.performance import PerformanceAnalyser
from systematic_trading.analysis.walk_forward import WalkForwardValidator

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

# ── 1. Moving Average Crossover — parameter sweep ─────────────────────────────

print("\n" + "=" * 60)
print("  DEMO 1: Moving Average Crossover — Parameter Sweep")
print("  Ticker: NVDA  |  Period: 2020-01-01 → 2024-01-01")
print("=" * 60)

ticker = "NVDA"
start = "2020-01-01"
end = "2024-01-01"

sweep_results = []
for short_w in [10, 20, 50]:
    for long_w in [50, 150, 200]:
        if short_w >= long_w:
            continue
        loader = DataLoader([ticker], start, end)
        strategy = MovingAverageCrossover(short_window=short_w, long_window=long_w)
        portfolio = Portfolio(initial_capital=100_000)
        engine = Engine(loader, strategy, portfolio)
        results = engine.run(ticker)
        analyser = PerformanceAnalyser(results, portfolio.trade_log)
        summary = analyser.summary()
        sweep_results.append({"short": short_w, "long": long_w, **summary})

df = pd.DataFrame(sweep_results).sort_values("total_return", ascending=False)
print(df.to_string(index=False))


# ── 2. Pairs Trading ──────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("  DEMO 2: Pairs Trading (Engle-Granger cointegration)")
print("  Pair: KO / PEP  |  Period: 2015-01-01 → 2024-01-01")
print("=" * 60)

pair_tickers = ["KO", "PEP"]
pair_loader = DataLoader(pair_tickers, "2015-01-01", "2024-01-01")
pair_strategy = PairsTrading(window=60, z_entry=2.0)
pair_portfolio = Portfolio(initial_capital=100_000)
pair_engine = PairsEngine(pair_loader, pair_strategy, pair_portfolio)

pair_results = pair_engine.run("KO", "PEP")

print(f"Cointegrated: {pair_strategy.is_cointegrated}  |  p-value: {pair_strategy.coint_pvalue:.4f}")
print(f"Hedge ratio (KO = h * PEP): {pair_strategy.hedge_ratio:.4f}")

pair_analyser = PerformanceAnalyser(pair_results, pair_portfolio.trade_log)
pair_summary = pair_analyser.summary()
for k, v in pair_summary.items():
    print(f"  {k}: {v}")


# ── 3. Walk-Forward Validation ────────────────────────────────────────────────

print("\n" + "=" * 60)
print("  DEMO 3: Walk-Forward Validation (7yr train / 3yr test)")
print("  Strategy: MA Crossover(20, 150) on NVDA  |  2010-2023")
print("=" * 60)

wfv = WalkForwardValidator(
    strategy_class=MovingAverageCrossover,
    strategy_params={"short_window": 20, "long_window": 150},
    ticker="NVDA",
    start="2010-01-01",
    end="2023-01-01",
    train_years=7,
    test_years=3,
    initial_capital=100_000,
)

wf_df = wfv.run()
cols = ["test_start", "test_end", "total_return", "sharpe_ratio", "cagr", "max_drawdown"]
print(wf_df[cols].to_string(index=False))
