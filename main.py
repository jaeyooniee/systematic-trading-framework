from systematic_trading.data.data_loader import DataLoader
from systematic_trading.strategies.moving_average import MovingAverageCrossover

loader = DataLoader(["AAPL", "MSFT"], "2023-01-01", "2026-06-11")

prices = loader.get_prices()
print("Prices: ")
print(prices.head())

returns = loader.get_returns()
print("\nReturns: ")
print(returns.head())

strategy = MovingAverageCrossover(short_window=20, long_window=50)
signals = strategy.generate_signals(prices["AAPL"])
print("\nMoving Average Signals: ")
print(signals.tail())