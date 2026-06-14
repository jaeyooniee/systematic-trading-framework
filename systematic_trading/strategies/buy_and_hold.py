import pandas as pd

class BuyAndHold:
    def generate_signals(self, prices):
        signals = pd.Series(0, index=prices.index)
        signals.iloc[0] = 1

        return signals