import numpy as np
import pandas as pd
import pytest

from systematic_trading.analysis.performance import PerformanceAnalyser


@pytest.fixture
def sample_results():
    np.random.seed(99)
    dates = pd.date_range("2020-01-02", periods=504, freq="B")
    values = 100_000 * np.cumprod(1 + np.random.randn(504) * 0.008)
    prices = 100 * np.cumprod(1 + np.random.randn(504) * 0.01)
    return [
        {"date": d, "portfolio_value": float(v), "price": float(p)}
        for d, v, p in zip(dates, values, prices)
    ]


@pytest.fixture
def trade_log_fixture():
    return [
        {"side": "BUY",  "ticker": "AAPL", "total_cost": 10_000},
        {"side": "SELL", "ticker": "AAPL", "total_proceeds": 11_000},  # win
        {"side": "BUY",  "ticker": "AAPL", "total_cost": 10_000},
        {"side": "SELL", "ticker": "AAPL", "total_proceeds":  9_000},  # loss
        {"side": "BUY",  "ticker": "AAPL", "total_cost": 10_000},
        {"side": "SELL", "ticker": "AAPL", "total_proceeds": 12_000},  # win
    ]


# ---- total_return -------------------------------------------------------

def test_total_return_formula(sample_results):
    analyser = PerformanceAnalyser(sample_results)
    start = sample_results[0]["portfolio_value"]
    end = sample_results[-1]["portfolio_value"]
    assert abs(analyser.total_return() - (end / start - 1)) < 1e-9


# ---- max_drawdown -------------------------------------------------------

def test_max_drawdown_non_positive(sample_results):
    analyser = PerformanceAnalyser(sample_results)
    assert analyser.max_drawdown() <= 0


# ---- sharpe_ratio -------------------------------------------------------

def test_sharpe_ratio_is_float(sample_results):
    analyser = PerformanceAnalyser(sample_results)
    assert isinstance(analyser.sharpe_ratio(), float)


# ---- cagr ---------------------------------------------------------------

def test_cagr_positive_when_growth(sample_results):
    results = list(sample_results)
    results[-1] = dict(results[-1])
    results[-1]["portfolio_value"] = results[0]["portfolio_value"] * 1.5
    assert PerformanceAnalyser(results).cagr() > 0

def test_cagr_negative_when_loss(sample_results):
    results = list(sample_results)
    results[-1] = dict(results[-1])
    results[-1]["portfolio_value"] = results[0]["portfolio_value"] * 0.5
    assert PerformanceAnalyser(results).cagr() < 0


# ---- bootstrap_sharpe_ci ------------------------------------------------

def test_bootstrap_ci_lower_lt_upper(sample_results):
    lower, upper = PerformanceAnalyser(sample_results).bootstrap_sharpe_ci(n_bootstrap=1000)
    assert lower < upper

def test_bootstrap_ci_contains_point_estimate(sample_results):
    analyser = PerformanceAnalyser(sample_results)
    point = analyser.sharpe_ratio()
    lower, upper = analyser.bootstrap_sharpe_ci(n_bootstrap=2000)
    # The point estimate should be close to the centre of the CI
    assert lower < point < upper


# ---- win_rate -----------------------------------------------------------

def test_win_rate_range(sample_results, trade_log_fixture):
    analyser = PerformanceAnalyser(sample_results, trade_log_fixture)
    wr = analyser.win_rate()
    assert wr is not None
    assert 0.0 <= wr <= 1.0

def test_win_rate_value(sample_results, trade_log_fixture):
    analyser = PerformanceAnalyser(sample_results, trade_log_fixture)
    # 2 wins out of 3 round trips
    assert abs(analyser.win_rate() - 2 / 3) < 1e-9

def test_win_rate_none_without_trade_log(sample_results):
    analyser = PerformanceAnalyser(sample_results)
    assert analyser.win_rate() is None


# ---- summary ------------------------------------------------------------

def test_summary_keys(sample_results, trade_log_fixture):
    analyser = PerformanceAnalyser(sample_results, trade_log_fixture)
    s = analyser.summary()
    for key in ("total_return", "max_drawdown", "sharpe_ratio", "cagr",
                "sortino_ratio", "win_rate", "sharpe_ci_95"):
        assert key in s

def test_summary_sharpe_ci_is_tuple(sample_results):
    s = PerformanceAnalyser(sample_results).summary()
    assert isinstance(s["sharpe_ci_95"], tuple)
    assert len(s["sharpe_ci_95"]) == 2
