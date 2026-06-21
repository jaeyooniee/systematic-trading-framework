import pytest
from systematic_trading.engine.portfolio import Portfolio


@pytest.fixture
def portfolio():
    return Portfolio(initial_capital=100_000)


# ---- Initialisation ----------------------------------------------------

def test_initial_cash(portfolio):
    assert portfolio.cash == 100_000

def test_initial_positions_empty(portfolio):
    assert portfolio.positions == {}

def test_initial_trade_log_empty(portfolio):
    assert portfolio.trade_log == []


# ---- Long trades (execute_trade) ---------------------------------------

def test_buy_creates_position(portfolio):
    portfolio.execute_trade("AAPL", 1, 100.0, "2024-01-02")
    assert portfolio.positions.get("AAPL", 0) > 0

def test_buy_reduces_cash(portfolio):
    portfolio.execute_trade("AAPL", 1, 100.0, "2024-01-02")
    assert portfolio.cash < 100_000

def test_sell_closes_position(portfolio):
    portfolio.execute_trade("AAPL", 1, 100.0, "2024-01-02")
    portfolio.execute_trade("AAPL", -1, 110.0, "2024-01-10")
    assert portfolio.positions.get("AAPL", 0) == 0

def test_commission_applied_on_buy(portfolio):
    portfolio.execute_trade("AAPL", 1, 100.0, "2024-01-02")
    trade = portfolio.trade_log[0]
    assert trade["commission"] > 0

def test_no_double_buy(portfolio):
    portfolio.execute_trade("AAPL", 1, 100.0, "2024-01-02")
    shares_after_first = portfolio.positions["AAPL"]
    portfolio.execute_trade("AAPL", 1, 100.0, "2024-01-03")
    assert portfolio.positions["AAPL"] == shares_after_first

def test_portfolio_value_increases_with_price(portfolio):
    portfolio.execute_trade("AAPL", 1, 100.0, "2024-01-02")
    val_low = portfolio.get_portfolio_value({"AAPL": 100.0})
    val_high = portfolio.get_portfolio_value({"AAPL": 200.0})
    assert val_high > val_low


# ---- Short selling (_enter_short / _close_position) --------------------

def test_short_increases_cash(portfolio):
    cash_before = portfolio.cash
    portfolio._enter_short("TSLA", 200.0, 5000.0, "2024-01-02")
    assert portfolio.cash > cash_before

def test_short_creates_negative_position(portfolio):
    portfolio._enter_short("TSLA", 200.0, 5000.0, "2024-01-02")
    assert portfolio.positions.get("TSLA", 0) < 0

def test_cover_clears_short(portfolio):
    portfolio._enter_short("TSLA", 200.0, 5000.0, "2024-01-02")
    portfolio._close_position("TSLA", 190.0, "2024-01-10")
    assert portfolio.positions.get("TSLA", 0) == 0

def test_short_profit_when_price_falls(portfolio):
    portfolio._enter_short("TSLA", 200.0, 10000.0, "2024-01-02")
    val_at_200 = portfolio.get_portfolio_value({"TSLA": 200.0})
    val_at_150 = portfolio.get_portfolio_value({"TSLA": 150.0})
    assert val_at_150 > val_at_200


# ---- Pairs trade -------------------------------------------------------

def test_pairs_trade_enters_both_legs(portfolio):
    portfolio.execute_pairs_trade("MSFT", "GOOG", 1, 300.0, 150.0, "2024-01-02")
    pos_msft = portfolio.positions.get("MSFT", 0)
    pos_goog = portfolio.positions.get("GOOG", 0)
    assert pos_msft > 0    # long
    assert pos_goog < 0    # short

def test_pairs_trade_exits_on_zero_signal(portfolio):
    portfolio.execute_pairs_trade("MSFT", "GOOG", 1, 300.0, 150.0, "2024-01-02")
    portfolio.execute_pairs_trade("MSFT", "GOOG", 0, 305.0, 148.0, "2024-01-10")
    assert portfolio.positions.get("MSFT", 0) == 0
    assert portfolio.positions.get("GOOG", 0) == 0
