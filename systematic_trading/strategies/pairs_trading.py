import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import coint


class PairsTrading:
    """
    Pairs Trading via Engle-Granger cointegration test and rolling z-score signals.

    Signal = 1:  buy spread  (long A, short B) when z-score < -z_entry
    Signal = -1: sell spread (short A, long B) when z-score > z_entry
    Signal = 0:  flat
    """

    def __init__(self, window=60, z_entry=2.0, z_exit=0.5):
        self.window = window
        self.z_entry = z_entry
        self.z_exit = z_exit
        self.hedge_ratio = None
        self.is_cointegrated = False
        self.coint_pvalue = None

    def test_cointegration(self, prices_a, prices_b):
        """
        Engle-Granger cointegration test (hypothesis testing on two price series).
        Returns (is_cointegrated: bool, p_value: float).
        """
        _, pvalue, _ = coint(prices_a.values, prices_b.values)
        self.coint_pvalue = pvalue
        self.is_cointegrated = bool(pvalue < 0.05)
        return self.is_cointegrated, pvalue

    def generate_signals(self, prices_a, prices_b):
        """
        OLS hedge ratio -> spread -> rolling z-score -> entry signals.

        Returns:
            signals : pd.Series of {-1, 0, 1}
            z_score : pd.Series of rolling z-score values
        """
        # Hedge ratio via OLS: prices_a ~ hedge_ratio * prices_b + intercept
        self.hedge_ratio = float(np.polyfit(prices_b.values, prices_a.values, 1)[0])
        spread = prices_a - self.hedge_ratio * prices_b

        rolling_mean = spread.rolling(self.window).mean()
        rolling_std = spread.rolling(self.window).std()
        z_score = (spread - rolling_mean) / rolling_std

        signals = pd.Series(0, index=prices_a.index)
        signals[z_score < -self.z_entry] = 1
        signals[z_score > self.z_entry] = -1

        return signals, z_score
