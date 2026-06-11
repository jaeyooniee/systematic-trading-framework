import pandas as pd

class MovingAverageCrossover:
    """
    the class contains two modules

    1. __init__(self, short_window, long_window)
    2. generate_signals(self, prices)

    the goal is to find golden and dead cross (default: 50MA, 200MA).
    this class uses moving average strategy.
    
    """

    def __init__(self, short_window=50, long_window=200):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, prices):
        """
        the module generates signals by simply checking which ma crosses the other
        
        """
        short_ma = prices.rolling(self.short_window).mean()
        long_ma = prices.rolling(self.long_window).mean()

        signals = pd.Series(0, index=prices.index)

        signals[short_ma > long_ma] = 1
        signals[short_ma < long_ma] = -1

        return signals