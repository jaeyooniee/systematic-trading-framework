class Portfolio:
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}
        self.trade_log = []

    def execute_trade(self, ticker, signal, price, date):
        if signal == 1:
            buy_amount = self.cash * 0.1 # assign buy amount proportion
            buy_volume = buy_amount // price # number of shares

            if buy_volume > 0:
                cost = buy_volume * price
                self.cash -= cost
                self.positions[ticker] = int(self.positions.get(ticker, 0) + buy_volume)
                self.trade_log.append({
                    "date": date,
                    "ticker": ticker,
                    "side": "BUY",
                    "volume": int(buy_volume),
                    "price": price
                })

        elif signal == -1:
            sell_volume = self.positions.get(ticker, 0)

            if sell_volume > 0:
                sell_amount = sell_volume * price
                self.cash += sell_amount
                self.positions[ticker] = 0
                self.trade_log.append({
                    "date": date,
                    "ticker": ticker,
                    "side": "SELL",
                    "volume": sell_volume,
                    "price": price
                })

    def get_portfolio_value(self, prices):
        total_value = self.cash

        for ticker, volume in self.positions.items():
            curr_price = prices[ticker]
            total_value += volume * curr_price

        return total_value
                



