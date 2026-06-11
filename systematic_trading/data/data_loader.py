import pandas as pd
import yfinance as yf

class DataLoader:
    """
    'DataLoader' class consists of three modules: 

    1. __init__(self, tickers: list[str], start:str, end: str)
    2. get_prices(self)
    3. get_returns(self)

    """

    def __init__(self, tickers: list[str], start: str, end: str):
        self.tickers = tickers
        self.start = start
        self.end = end
        self.data = None

    def get_prices(self):
        """
        it returns the adjusted close price data of the input tickers while it drops NaN values
        
        """
        raw_data = yf.download(self.tickers, start=self.start, end=self.end, auto_adjust=False, progress=False)

        prices = raw_data["Adj Close"]
        prices = prices.dropna()

        self.data = prices

        return prices
    
    def get_returns(self):
        """
        we get the daily return of the tickers 
        
        """
        if self.data is None:
            self.get_prices()

        returns = self.data.pct_change().dropna()

        return returns