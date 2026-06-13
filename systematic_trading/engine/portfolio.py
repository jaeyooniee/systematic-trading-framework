class Portfolio:
    def __init__(self, initial_capital=100000, commission=0.001, slippage=0.0005, risk_per_trade=0.01):
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.risk_per_trade = risk_per_trade
        self.cash = initial_capital
        self.positions = {}
        self.trade_log = []

    def execute_trade(self, ticker, signal, price, date):
        if signal == 1:
            current_volume = self.positions.get(ticker, 0)

            if current_volume == 0:
                portfolio_value = self.cash
                trade_budget = min(portfolio_value * self.risk_per_trade, self.cash)
                buy_price = price * (1 + self.slippage)

                cost_per_share = buy_price * (1 + self.commission)
                buy_volume = int(trade_budget // cost_per_share)

                if buy_volume > 0:
                    trade_value = buy_price * buy_volume
                    commission_cost = trade_value * self.commission
                    total_cost = trade_value + commission_cost

                    self.cash -= total_cost
                    self.positions[ticker] = buy_volume

                    self.trade_log.append({
                        "date": date,
                        "ticker": ticker,
                        "side": "BUY",
                        "volume": buy_volume,
                        "price": price,
                        "executed_price": buy_price,
                        "trade_price": trade_value,
                        "commission": commission_cost,
                        "total_cost": total_cost
                    })


        elif signal == -1:
            sell_volume = self.positions.get(ticker, 0)

            if sell_volume > 0:
                sell_price = price * (1 - self.slippage)

                trade_value = sell_price * sell_volume
                commission_cost = trade_value * self.commission

                # total returns I get is the yields - commission.
                total_proceeds = trade_value - commission_cost
                self.cash += total_proceeds
                self.positions[ticker] = 0

                self.trade_log.append({
                    "date": date,
                    "ticker": ticker,
                    "side": "SELL",
                    "volume": sell_volume,
                    "price": price,
                    "executed_price": sell_price,
                    "trade_value": trade_value, 
                    "commission": commission_cost,
                    "total_proceeds": total_proceeds
                })


    def get_portfolio_value(self, prices):
        total_value = self.cash

        for ticker, volume in self.positions.items():
            curr_price = prices[ticker]
            total_value += volume * curr_price

        return total_value
                



