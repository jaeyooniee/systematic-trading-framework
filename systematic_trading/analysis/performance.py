import pandas as pd
import numpy as np

class PerformanceAnalyser:
    def __init__(self, results):
        self.results = pd.DataFrame(results)
        self.returns = self.results["portfolio_value"].pct_change().dropna()

    # the methods below return portfolio values from a selected strategy

    def total_return(self):
        start_value = self.results["portfolio_value"].iloc[0]
        end_value = self.results["portfolio_value"].iloc[-1]

        return (end_value / start_value) - 1
    
    def max_drawdown(self):
        portfolio_values = self.results["portfolio_value"]
        rolling_peak = portfolio_values.cummax()
        drawdown = (portfolio_values - rolling_peak) / rolling_peak

        return drawdown.min()
    
    # Now we need the returns and drawdowns when we buy and hold the stocks
    
    def buy_and_hold_return(self):
        start_price = self.results["price"].iloc[0]
        end_price = self.results["price"].iloc[-1]

        return (end_price / start_price) - 1
    
    def buy_and_hold_max_drawdown(self):
        prices = self.results["price"]
        rolling_peak = prices.cummax()
        drawdown = (prices-rolling_peak) / rolling_peak

        return drawdown.min()
    
    # strategy alpha comparators
    # 1. sharpe ratio
    # 2. 
    
    def sharpe_ratio(self):
        mean_return = self.returns.mean()
        volatility = self.returns.std()

        if volatility == 0:
            return 0
        
        return (mean_return / volatility) * np.sqrt(252)
    
    def cagr(self):
        start_value = self.results["portfolio_value"].iloc[0]
        end_value = self.results["portfolio_value"].iloc[-1]

        start_date = self.results["date"].iloc[0]
        end_date = self.results["date"].iloc[-1]

        total_days = (end_date - start_date).days
        years = total_days / 365

        return (end_value / start_value) ** (1 / years) - 1
    
    def summary(self):
        return {
            "total_return": round(float(self.total_return())*100, 2),
            "max_drawdown": round(float(self.max_drawdown())*100, 2),
            "sharpe_ratio": round(float(self.sharpe_ratio()), 2),
            "cagr": round(float(self.cagr()) * 100, 2),
            "buy_and_hold_return": round(float(self.buy_and_hold_return()) * 100, 2),
            "excess_return": round(float((self.total_return() - self.buy_and_hold_return())) * 100, 2),
            "buy_and_hold_max_drawdown": round(float(self.buy_and_hold_max_drawdown()) * 100, 2)
        }
