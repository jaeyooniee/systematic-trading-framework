import pandas as pd


class PairsEngine:
    """
    Backtesting engine for pairs trading strategies.
    Handles two-ticker long/short positions via the portfolio.
    """

    def __init__(self, data_loader, strategy, portfolio):
        self.data_loader = data_loader
        self.strategy = strategy
        self.portfolio = portfolio

    def run(self, ticker_a, ticker_b):
        """
        Runs the pairs backtest and returns a list of daily result dicts.

        Args:
            ticker_a : primary ticker (reference price tracked in results)
            ticker_b : secondary ticker

        Returns:
            list of dicts with keys: date, portfolio_value, cash, signal, price, z_score
        """
        prices = self.data_loader.get_prices()
        prices_a = prices[ticker_a]
        prices_b = prices[ticker_b]

        self.strategy.test_cointegration(prices_a, prices_b)
        signals, z_score = self.strategy.generate_signals(prices_a, prices_b)

        results = []

        for date in prices_a.index:
            p_a = prices_a.loc[date]
            p_b = prices_b.loc[date]
            sig = signals.loc[date]
            z = z_score.loc[date]

            self.portfolio.execute_pairs_trade(ticker_a, ticker_b, sig, p_a, p_b, date)

            portfolio_value = self.portfolio.get_portfolio_value(
                {ticker_a: p_a, ticker_b: p_b}
            )

            results.append({
                "date": date,
                "portfolio_value": portfolio_value,
                "cash": self.portfolio.cash,
                "signal": sig,
                "price": p_a,
                "z_score": float(z) if pd.notna(z) else 0.0,
            })

        return results
