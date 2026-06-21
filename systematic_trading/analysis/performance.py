import numpy as np
import pandas as pd


class PerformanceAnalyser:
    def __init__(self, results, trade_log=None):
        self.results = pd.DataFrame(results)
        self.returns = self.results["portfolio_value"].pct_change().dropna()
        self.trade_log = trade_log or []

    def total_return(self):
        start_value = self.results["portfolio_value"].iloc[0]
        end_value = self.results["portfolio_value"].iloc[-1]
        return (end_value / start_value) - 1

    def max_drawdown(self):
        portfolio_values = self.results["portfolio_value"]
        rolling_peak = portfolio_values.cummax()
        drawdown = (portfolio_values - rolling_peak) / rolling_peak
        return drawdown.min()

    def buy_and_hold_return(self):
        start_price = self.results["price"].iloc[0]
        end_price = self.results["price"].iloc[-1]
        return (end_price / start_price) - 1

    def buy_and_hold_max_drawdown(self):
        prices = self.results["price"]
        rolling_peak = prices.cummax()
        drawdown = (prices - rolling_peak) / rolling_peak
        return drawdown.min()

    def sharpe_ratio(self):
        mean_return = self.returns.mean()
        volatility = self.returns.std()
        if volatility == 0:
            return 0
        return (mean_return / volatility) * 252 ** 0.5

    def cagr(self):
        start_value = self.results["portfolio_value"].iloc[0]
        end_value = self.results["portfolio_value"].iloc[-1]
        start_date = self.results["date"].iloc[0]
        end_date = self.results["date"].iloc[-1]
        years = (end_date - start_date).days / 365.25
        if years <= 0:
            return 0
        return (end_value / start_value) ** (1 / years) - 1

    def sortino_ratio(self, target_return=0):
        excess_returns = self.returns - target_return
        downside_returns = excess_returns.clip(upper=0)
        downside_deviation = (downside_returns ** 2).mean() ** 0.5
        if downside_deviation == 0:
            return 0
        return (excess_returns.mean() / downside_deviation) * 252 ** 0.5

    def win_rate(self):
        """Fraction of profitable round-trip trades from the trade log."""
        if not self.trade_log:
            return None

        # Pair BUY -> SELL (or SHORT -> COVER) per ticker, in chronological order
        buys = {}   # ticker -> list of total_cost
        wins = 0
        total = 0

        for trade in self.trade_log:
            side = trade.get("side")
            ticker = trade.get("ticker")

            if side in ("BUY",):
                buys.setdefault(ticker, []).append(trade.get("total_cost", 0))

            elif side in ("SELL",):
                cost_queue = buys.get(ticker, [])
                if cost_queue:
                    cost = cost_queue.pop(0)
                    proceeds = trade.get("total_proceeds", 0)
                    total += 1
                    if proceeds > cost:
                        wins += 1

            elif side == "SHORT":
                buys.setdefault(ticker + "_short", []).append(
                    trade.get("total_proceeds", 0)
                )

            elif side == "COVER":
                key = ticker + "_short"
                cost_queue = buys.get(key, [])
                if cost_queue:
                    initial_proceeds = cost_queue.pop(0)
                    cover_cost = trade.get("total_cost", 0)
                    total += 1
                    if initial_proceeds > cover_cost:
                        wins += 1

        return wins / total if total > 0 else None

    def bootstrap_sharpe_ci(self, n_bootstrap=10000, confidence=0.95):
        """
        Bootstrap 95% confidence interval for the annualised Sharpe ratio.
        Resamples daily returns 10,000 times and returns (lower, upper).
        """
        returns = self.returns.values
        n = len(returns)

        # Vectorised bootstrap: draw all samples at once
        idx = np.random.randint(0, n, size=(n_bootstrap, n))
        samples = returns[idx]

        means = samples.mean(axis=1)
        stds = samples.std(axis=1)

        with np.errstate(divide="ignore", invalid="ignore"):
            sharpe_dist = np.where(stds > 0, (means / stds) * np.sqrt(252), 0.0)

        alpha = 1 - confidence
        lower = float(np.percentile(sharpe_dist, alpha / 2 * 100))
        upper = float(np.percentile(sharpe_dist, (1 - alpha / 2) * 100))

        return lower, upper

    def summary(self):
        base = {
            "total_return": round(float(self.total_return()) * 100, 2),
            "max_drawdown": round(float(self.max_drawdown()) * 100, 2),
            "sharpe_ratio": round(float(self.sharpe_ratio()), 2),
            "cagr": round(float(self.cagr()) * 100, 2),
            "sortino_ratio": round(float(self.sortino_ratio()), 2),
        }

        wr = self.win_rate()
        if wr is not None:
            base["win_rate"] = round(wr * 100, 1)

        lower, upper = self.bootstrap_sharpe_ci()
        base["sharpe_ci_95"] = (round(lower, 2), round(upper, 2))

        return base
