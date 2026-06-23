⚠️ **DEPRECATED**: This repository is no longer maintained. Please use [New-Repo-Link] instead.

# Systematic Trading Framework

- Currently on break to study strategies and their backgrounds before tailoring them into my project.

Python-based systematic equity backtesting framework for comparing trading
strategies on the same universe, execution assumptions, benchmark set and
statistical validation process.

The MVP goal is not to force a strategy to beat the benchmark. The goal is to
build a clean research pipeline that answers three questions:

- Did the strategy run correctly?
- Did it beat the same-universe equal-weight buy-and-hold benchmark?
- Does the excess return look statistically meaningful, or could it easily be
  noise?

## MVP Scope

The current MVP does four things:

1. Selects a fixed-seed random Nasdaq common-stock universe.
2. Runs several strategy families on the same data and execution engine.
3. Selects each strategy family's hyperparameters on validation data only.
4. Evaluates the selected strategies on train, validation and final test periods.

The final test period is reserved for out-of-sample evaluation. It is not used
for model fitting, hyperparameter selection or universe data-quality filtering.

## Data Pipeline

- Universe source: Nasdaq listed symbols file.
- Universe filter: common stocks only, excluding ETFs, warrants, rights, units,
  preferred shares, notes and test issues.
- Universe selection: fixed random seed for reproducibility.
- Price source: `yfinance` adjusted close prices.
- Metadata source: `yfinance` sector and industry data.
- Metadata cache: `data/ticker_metadata.csv`.

Data cleaning is handled by `DataLoader`:

- tickers with excessive missing values are removed,
- short internal missing-price gaps are interpolated,
- tickers with remaining edge missing values are removed,
- data-quality reports show missing data, excluded tickers and interpolation use.
- final strategy runs require all requested tickers to survive cleaning, so the
  universe cannot silently shrink during evaluation.

To avoid test-period leakage, the random universe data-quality filter uses only
the train-side data window.

## Time Split

The current split is:

```text
Train:      2023-01-01 to 2025-01-01
Validation: 2025-01-01 to 2026-01-01
Test:       2026-01-01 to 2026-06-22
```

The code checks that these periods do not overlap. Rolling strategies may load
prior-period price history as warm-up data, but trades and performance snapshots
start only at the evaluation period start. This avoids initial rolling-window
`NaN` behaviour without using future information.

The test end date is fixed for reproducibility. In `yfinance`, the end date is
exclusive, so this asks for data up to the last available trading day before
2026-06-22.

## Strategy Optimization

Candidate hyperparameters are created before final evaluation. Each candidate is
evaluated across walk-forward validation folds before the final comparison.
The current validation folds are:

```text
Fold 1: evaluate 2024 using prior data as warm-up
Fold 2: evaluate 2025 using prior data as warm-up
Final diagnostic test: 2026-01-01 to 2026-06-22
```

Only the best candidate from each strategy family is sent to the final
comparison.

Selection uses:

1. average Sharpe across validation folds,
2. stability penalty for uneven fold Sharpe,
3. drawdown penalty,
4. turnover penalty,
5. penalty for folds with non-positive Sharpe or return.

The test period is not used to choose parameters.

If the best candidate in a strategy family fails the walk-forward pass rule, it
is still reported for diagnostics but is labelled `Rejected Validation`. This
prevents a strategy from being accepted just because it looks good in one
validation year or later in the test period.

## Strategies

### Equal Weight Buy and Hold

Internal benchmark. It buys the selected universe at equal initial dollar weight
and then holds the positions.

### Linear Pairs Trading

Searches for cointegrated equity pairs and estimates a linear spread:

```text
spread = stock A price - (intercept + hedge_ratio * stock B price)
```

The strategy enters long-short positions when the spread z-score moves far from
its rolling mean and exits when it reverts near the mean. Pair selection is
filtered by sector metadata, return correlation, cointegration p-value and
multiple-testing correction.

This is intentionally treated as a testable approximation. It may underfit real
equity relationships because company relationships can be nonlinear and unstable.

### Momentum

Ranks stocks by historical price momentum and invests in the top 25% of the
universe. The current implementation can skip the most recent days when
calculating momentum to reduce short-term reversal noise. Candidate variants
also test score-weighted and volatility-adjusted momentum, so stronger signals
can receive larger weights while very noisy winners are penalized. Momentum also
supports a maximum single-stock weight cap and a same-universe market-regime
filter, which turns the signal off when the equal-weight universe index is below
its long moving average.

### Weighted Moving Average

Holds stocks whose short moving average is above their long moving average.
Active stocks are equally weighted. Candidate variants can require the moving
average condition to persist for several days before the stock becomes active,
which reduces one-day crossover noise.

### Weighted RSI Mean Reversion

Buys stocks after oversold RSI signals and exits when RSI recovers toward a
neutral or upper threshold. Candidate variants include the original daily
equal-weight version and a more defensive version with weekly rebalancing, a
maximum single-stock weight cap and a trend filter that only allows mean-
reversion entries when the stock remains above its long moving average. The
search also tests less extreme pullback thresholds, such as RSI 40 or 45, because
waiting only for RSI 30 can create sparse, concentrated trades.

## Benchmarks

The final comparison includes:

- Equal Weight Buy and Hold on the selected 45-stock universe.

This is the main benchmark because every active strategy uses the same 45-stock
universe. The comparison asks whether the strategy adds value over simply buying
the same stocks at equal initial weights and holding them.

## Performance Metrics

The framework reports:

- total return,
- CAGR,
- Sharpe ratio,
- bootstrap Sharpe confidence interval,
- Sortino ratio,
- Calmar ratio,
- maximum drawdown,
- maximum absolute daily return,
- near-zero portfolio-value and extreme-return diagnostics,
- turnover,
- win rate,
- number of executions,
- final cash,
- product-level PnL contribution.

## Statistical Validation

The framework tests daily excess returns against each benchmark using:

- simple daily excess-return t-style test,
- Newey-West adjusted standard errors,
- block bootstrap mean test,
- rolling excess-return validation.

The result is classified as:

- `robust_positive`: Newey-West and block bootstrap both support positive excess,
- `robust_negative`: both support negative excess,
- `weak_positive`: simple significance plus supportive rolling behaviour,
- `weak_negative`: simple significance plus weak rolling behaviour,
- `inconclusive`: insufficient statistical evidence.

This matters because a positive backtest return alone does not prove alpha.
Financial returns are noisy, autocorrelated and volatility-clustered.

## Current Limitations

- The universe is a random current Nasdaq common-stock sample, not a fully
  point-in-time historical index membership database.
- Execution uses adjusted close prices and fixed slippage.
- Active strategies use a no-trade band to avoid rebalancing tiny daily weight
  drift. Exact benchmarks keep their intended benchmark definitions.
- Short-sale proceeds are held as restricted collateral rather than reusable
  free cash, but borrow fees, margin interest and forced buy-ins are not modelled.
- Rebalancing uses integer share quantities, so small cash residuals and minor
  order effects can remain when many positions are adjusted at once.
- Performance metrics are not winsorized. If daily returns become extreme or
  portfolio value approaches zero, the framework flags the result rather than
  silently clipping the data.
- Sector and industry metadata depends on `yfinance` quality.
- Linear pairs trading is a simplified model and may miss nonlinear
  relationships.
- Current long-short pairs weights do not guarantee beta-neutral or
  factor-neutral exposure.
- The test period should stay protected after it has been reviewed.
- Prior-period price history may be used for rolling-indicator warm-up, but it is
  not used for hyperparameter selection or model refitting inside the test run.

## Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the backtest:

```bash
python main.py
```
