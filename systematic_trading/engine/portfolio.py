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
            # negative volume (short position) correctly reduces portfolio value
            total_value += volume * curr_price

        return total_value

    # ------------------------------------------------------------------ #
    # Pairs trading helpers — short selling support                        #
    # ------------------------------------------------------------------ #

    def _enter_long(self, ticker, price, budget, date):
        exec_price = price * (1 + self.slippage)
        qty = int(budget // (exec_price * (1 + self.commission)))
        if qty <= 0:
            return
        total_cost = exec_price * qty * (1 + self.commission)
        self.cash -= total_cost
        self.positions[ticker] = self.positions.get(ticker, 0) + qty
        self.trade_log.append({
            "date": date, "ticker": ticker, "side": "BUY",
            "volume": qty, "price": price,
            "executed_price": exec_price, "total_cost": total_cost,
        })

    def _enter_short(self, ticker, price, budget, date):
        exec_price = price * (1 - self.slippage)
        qty = int(budget // (exec_price * (1 + self.commission)))
        if qty <= 0:
            return
        proceeds = exec_price * qty * (1 - self.commission)
        self.cash += proceeds
        self.positions[ticker] = self.positions.get(ticker, 0) - qty
        self.trade_log.append({
            "date": date, "ticker": ticker, "side": "SHORT",
            "volume": qty, "price": price,
            "executed_price": exec_price, "total_proceeds": proceeds,
        })

    def _close_position(self, ticker, price, date):
        qty = self.positions.get(ticker, 0)
        if qty == 0:
            return
        if qty > 0:
            exec_price = price * (1 - self.slippage)
            proceeds = exec_price * qty * (1 - self.commission)
            self.cash += proceeds
            self.trade_log.append({
                "date": date, "ticker": ticker, "side": "SELL",
                "volume": qty, "price": price,
                "executed_price": exec_price, "total_proceeds": proceeds,
            })
        else:
            qty_abs = abs(qty)
            exec_price = price * (1 + self.slippage)
            cost = exec_price * qty_abs * (1 + self.commission)
            self.cash -= cost
            self.trade_log.append({
                "date": date, "ticker": ticker, "side": "COVER",
                "volume": qty_abs, "price": price,
                "executed_price": exec_price, "total_cost": cost,
            })
        self.positions[ticker] = 0

    def execute_pairs_trade(self, ticker_a, ticker_b, signal, price_a, price_b, date):
        """
        Executes pairs trade signal:
          signal =  1 -> long A, short B  (buy the spread)
          signal = -1 -> short A, long B  (sell the spread)
          signal =  0 -> exit all positions
        """
        pos_a = self.positions.get(ticker_a, 0)
        current = 1 if pos_a > 0 else (-1 if pos_a < 0 else 0)

        # Exit if signal flipped or returning to flat
        if current != 0 and current != signal:
            self._close_position(ticker_a, price_a, date)
            self._close_position(ticker_b, price_b, date)
            current = 0

        # Enter new position
        if signal != 0 and current == 0:
            half_budget = self.cash * self.risk_per_trade / 2
            if signal == 1:
                self._enter_long(ticker_a, price_a, half_budget, date)
                self._enter_short(ticker_b, price_b, half_budget, date)
            else:
                self._enter_short(ticker_a, price_a, half_budget, date)
                self._enter_long(ticker_b, price_b, half_budget, date)
