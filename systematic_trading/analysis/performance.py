import pandas as pd

class PerformanceAnalyser:
    def __init__(self, results):
        self.results = pd.DataFrame(results)
        self.returns = self.results["portfolio_value"].pct_change().dropna()

    def total_return(self):
        start_value = self.results["portfolio_value"].iloc[0]
        end_value = self.results["portfolio_value"].iloc[-1]

        return (end_value / start_value) - 1
    
    def max_drawdown(self):
        portfolio_values = self.results["portfolio_value"]
        rolling_peak = portfolio_values.cummax()
        drawdown = (portfolio_values - rolling_peak) / rolling_peak

        return drawdown.min()
    
    def summary(self):
        return {
            "total_return": self.total_return(),
            "max_drawdown": self.max_drawdown()
        }