import numpy as np
import pandas as pd
import pytest

from systematic_trading.strategies.buy_and_hold import BuyAndHold
from systematic_trading.strategies.moving_average import MovingAverageCrossover
from systematic_trading.strategies.rsi_mean_reversion import RSIMeanReversion
from systematic_trading.strategies.pairs_trading import PairsTrading


@pytest.fixture
def sample_prices():
    np.random.seed(42)
    dates = pd.date_range("2018-01-01", periods=500, freq="B")
    prices = pd.Series(100 + np.cumsum(np.random.randn(500) * 1.5), index=dates)
    return prices


@pytest.fixture
def sample_pair(sample_prices):
    """Two cointegrated-ish price series."""
    np.random.seed(7)
    prices_b = sample_prices * 0.5 + np.random.randn(500) * 2
    return sample_prices, prices_b


# ---- BuyAndHold --------------------------------------------------------

def test_buy_and_hold_first_signal(sample_prices):
    signals = BuyAndHold().generate_signals(sample_prices)
    assert signals.iloc[0] == 1

def test_buy_and_hold_rest_zero(sample_prices):
    signals = BuyAndHold().generate_signals(sample_prices)
    assert (signals.iloc[1:] == 0).all()

def test_buy_and_hold_length(sample_prices):
    signals = BuyAndHold().generate_signals(sample_prices)
    assert len(signals) == len(sample_prices)


# ---- MovingAverageCrossover --------------------------------------------

def test_ma_signals_length(sample_prices):
    signals = MovingAverageCrossover(10, 50).generate_signals(sample_prices)
    assert len(signals) == len(sample_prices)

def test_ma_signals_valid_values(sample_prices):
    signals = MovingAverageCrossover(10, 50).generate_signals(sample_prices)
    assert set(signals.unique()).issubset({-1, 0, 1})


# ---- RSIMeanReversion --------------------------------------------------

def test_rsi_signals_length(sample_prices):
    signals = RSIMeanReversion().generate_signals(sample_prices)
    assert len(signals) == len(sample_prices)

def test_rsi_signals_valid_values(sample_prices):
    signals = RSIMeanReversion().generate_signals(sample_prices)
    assert set(signals.unique()).issubset({-1, 0, 1})


# ---- PairsTrading ------------------------------------------------------

def test_pairs_cointegration_returns_bool(sample_pair):
    a, b = sample_pair
    strategy = PairsTrading()
    is_coint, pvalue = strategy.test_cointegration(a, b)
    assert isinstance(is_coint, bool)
    assert 0.0 <= pvalue <= 1.0

def test_pairs_signals_length(sample_pair):
    a, b = sample_pair
    strategy = PairsTrading(window=30)
    signals, z = strategy.generate_signals(a, b)
    assert len(signals) == len(a)
    assert len(z) == len(a)

def test_pairs_signals_valid_values(sample_pair):
    a, b = sample_pair
    strategy = PairsTrading(window=30)
    signals, _ = strategy.generate_signals(a, b)
    assert set(signals.unique()).issubset({-1, 0, 1})

def test_pairs_hedge_ratio_set(sample_pair):
    a, b = sample_pair
    strategy = PairsTrading(window=30)
    strategy.generate_signals(a, b)
    assert strategy.hedge_ratio is not None
    assert strategy.hedge_ratio > 0
