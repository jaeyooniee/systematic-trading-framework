import pandas as pd


class MomentumStrategy:
    """
    Cross-sectional momentum: long top-decile stocks by 12-month trailing return,
    rebalanced monthly.

    generate_signals() accepts a multi-column prices DataFrame and returns a same-shape
    DataFrame of 0/1 signals.
    """

    def __init__(self, lookback_days=252, rebalance_freq="ME", top_pct=0.1):
        self.lookback_days = lookback_days
        self.rebalance_freq = rebalance_freq
        self.top_pct = top_pct

    def generate_signals(self, prices_df):
        """
        Args:
            prices_df : DataFrame (dates x tickers)

        Returns:
            signals_df : DataFrame of 0/1 signals, same shape as prices_df
        """
        signals = pd.DataFrame(0, index=prices_df.index, columns=prices_df.columns)
        rebalance_dates = prices_df.resample(self.rebalance_freq).last().index

        for i, rebal_date in enumerate(rebalance_dates):
            loc = prices_df.index.searchsorted(rebal_date, side="right") - 1
            if loc < self.lookback_days:
                continue

            window = prices_df.iloc[loc - self.lookback_days : loc + 1]
            trailing_returns = (window.iloc[-1] / window.iloc[0]) - 1

            n_top = max(1, int(len(prices_df.columns) * self.top_pct))
            top_tickers = trailing_returns.nlargest(n_top).index

            next_loc = (
                prices_df.index.searchsorted(rebalance_dates[i + 1], side="right") - 1
                if i + 1 < len(rebalance_dates)
                else len(prices_df)
            )

            for ticker in top_tickers:
                if ticker in signals.columns:
                    signals[ticker].iloc[loc:next_loc] = 1

        return signals
