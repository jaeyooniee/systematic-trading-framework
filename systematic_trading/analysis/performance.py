import pandas as pd
import numpy as np

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
            "total_return": round(float(self.total_return())*100, 2),
            "max_drawdown": round(float(self.max_drawdown())*100, 2),
            "sharpe_ratio": round(float(self.sharpe_ratio()), 2),
            "buy_and_hold_return": round(float(self.buy_and_hold_return()) * 100, 2),
            "excess_return": round(float((self.total_return() - self.buy_and_hold_return())) * 100, 2)
        }
    
    def sharpe_ratio(self):
        mean_return = self.returns.mean()
        volatility = self.returns.std()

        if volatility == 0:
            return 0
        
        return (mean_return / volatility) * np.sqrt(252)
    
    def buy_and_hold_return(self):
        start_price = self.results["price"].iloc[0]
        end_price = self.results["price"].iloc[-1]

        return (end_price / start_price) - 1
    
