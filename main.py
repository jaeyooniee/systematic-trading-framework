"""
the key role of main.py is to backtest the strategies in a single file.

"""
from systematic_trading.data.data_loader import DataLoader
from systematic_trading.strategies.moving_average import MovingAverageCrossover
from systematic_trading.engine.portfolio import Portfolio
from systematic_trading.engine.engine import Engine
from systematic_trading.analysis.performance import PerformanceAnalyser
import pandas as pd

ticker = "NVDA"
start = "2020-01-01"
end = "2024-01-01"
initial_capital = 100000

short_windows = [10, 20, 50]
long_windows = [50, 150, 200]

sweep_results = []

for short_window in short_windows:
    for long_window in long_windows:
        if short_window >= long_window:
            continue

        loader = DataLoader([ticker], start, end)
        strategy = MovingAverageCrossover(
            short_window=short_window,
            long_window=long_window
        )
        portfolio = Portfolio(initial_capital=initial_capital)
        engine = Engine(loader, strategy, portfolio)

        results = engine.run(ticker)

        analyser = PerformanceAnalyser(results)
        summary = analyser.summary()

        sweep_results.append({
            "short_window": short_window,
            "long_window": long_window,
            **summary
        })

sweep_df = pd.DataFrame(sweep_results)
sweep_df = sweep_df.sort_values("total_return", ascending=False)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

print(sweep_df)