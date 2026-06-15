import pandas as pd

class RSIMeanReversion:
    def __init__(self, window=14, lower_bound=30, upper_bound=70):
        self.window = window
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def generate_signals(self, prices):
        d = prices.diff()
        gain = d.clip(lower=0)
        loss = -d.clip(upper=0)

        avg_gain = gain.ewm(alpha=1/self.window, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/self.window, adjust=False).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        rsi = rsi.ffill().fillna(50)

        signals = pd.Series(0, index=prices.index)
        signals[rsi < self.lower_bound] = 1
        signals[rsi > self.upper_bound] = -1

        return signals
