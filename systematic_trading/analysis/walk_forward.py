import pandas as pd

from systematic_trading.data.data_loader import DataLoader
from systematic_trading.engine.engine import Engine
from systematic_trading.engine.portfolio import Portfolio
from systematic_trading.analysis.performance import PerformanceAnalyser


class WalkForwardValidator:
    """
    Walk-forward validation: train on train_years, test on test_years,
    slide the window forward by 1 year per fold.

    Proves strategies aren't overfit by measuring out-of-sample performance
    across multiple non-overlapping test periods.
    """

    def __init__(
        self,
        strategy_class,
        strategy_params,
        ticker,
        start,
        end,
        train_years=7,
        test_years=3,
        initial_capital=100000,
    ):
        self.strategy_class = strategy_class
        self.strategy_params = strategy_params
        self.ticker = ticker
        self.start = pd.Timestamp(start)
        self.end = pd.Timestamp(end)
        self.train_years = train_years
        self.test_years = test_years
        self.initial_capital = initial_capital

    def run(self):
        """
        Runs walk-forward folds and returns a DataFrame of out-of-sample metrics.

        Each row = one test fold with columns:
          train_start, train_end, test_start, test_end,
          total_return, max_drawdown, sharpe_ratio, cagr, sortino_ratio,
          win_rate, sharpe_ci_95
        """
        results = []
        train_start = self.start

        while True:
            train_end = train_start + pd.DateOffset(years=self.train_years)
            test_end = train_end + pd.DateOffset(years=self.test_years)

            if test_end > self.end:
                break

            loader = DataLoader(
                [self.ticker],
                train_end.strftime("%Y-%m-%d"),
                test_end.strftime("%Y-%m-%d"),
            )

            strategy = self.strategy_class(**self.strategy_params)
            portfolio = Portfolio(initial_capital=self.initial_capital)
            engine = Engine(loader, strategy, portfolio)

            try:
                fold_results = engine.run(self.ticker)
                analyser = PerformanceAnalyser(fold_results, portfolio.trade_log)
                summary = analyser.summary()
            except Exception:
                train_start += pd.DateOffset(years=1)
                continue

            summary["train_start"] = train_start.strftime("%Y-%m-%d")
            summary["train_end"] = train_end.strftime("%Y-%m-%d")
            summary["test_start"] = train_end.strftime("%Y-%m-%d")
            summary["test_end"] = test_end.strftime("%Y-%m-%d")
            results.append(summary)

            train_start += pd.DateOffset(years=1)

        return pd.DataFrame(results)
