class Engine:
    def __init__(self, data_loader, strategy, portfolio):
        self.data_loader = data_loader
        self.strategy = strategy
        self.portfolio = portfolio

    def run(self, ticker):
        price = self.data_loader.get_prices()
        ticker_prices = price[ticker]

        signals = self.strategy.generate_signals(ticker_prices)

        results = []

        for date in ticker_prices.index:
            price = ticker_prices.loc[date]
            signal = signals.loc[date]

            self.portfolio.execute_trade(ticker, signal, price, date)

            portfolio_value = self.portfolio.get_portfolio_value({ticker: price})

            results.append({
                "date": date,
                "portfolio_value": portfolio_value,
                "cash": self.portfolio.cash,
                "signal": signal,
                "price": price
            })

        return results
