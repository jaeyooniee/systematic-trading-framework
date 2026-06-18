import pandas as pd

class BuyAndHold:
    """
    This class represents 'buy/hold' strategy.
    We buy at the price of the start day and we aren't selling it. 
    """
    def generate_signals(self, prices):
        signals = pd.Series(0, index=prices.index)
        signals.iloc[0] = 1

        return signals


class EqualWeightRebalanced:
    def generate_target_weights(self, prices):
        target_weights = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)

        weight = 1.0 / len(prices.columns)
        target_weights.loc[:, prices.columns] = weight

        return target_weights
    

class EqualWeightBuyAndHold:
    def generate_target_weights(self, prices):
        initial_weights = pd.Series(1.0 / len(prices.columns), index=prices.columns)

        initial_prices = prices.iloc[0]
        shares_per_dollar = initial_weights / initial_prices

        position_values = prices.multiply(shares_per_dollar, axis=1)
        total_value = position_values.sum(axis=1)

        target_weights = position_values.div(total_value, axis=0)
        target_weights = target_weights.fillna(0.0)

        return target_weights