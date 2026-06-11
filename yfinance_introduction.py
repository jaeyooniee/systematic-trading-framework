import yfinance as yf

# Initialising a Ticker object (str | tuple(str, str) -> (symbol, market identifier code))
dat1 = yf.Ticker("MSFT")
dat2 = yf.Ticker(("OR", "XPAR"))


# print(dat.info)
# print(dat.calendar)
# print(dat.analyst_price_targets)
# print(dat.quarterly_income_stmt)
# print(dat.history(period='1mo'))
# print(dat.option_chain(dat.options[0]).calls)

tickers = yf.Tickers('MSFT AAPL GOOG')
print(tickers.tickers['MSFT'].info)
yf.download(['MSFT', 'AAPL', 'GOOG'], period='1mo')

spy = yf.Ticker('SPY').funds_data
print(spy.description)
print(spy.top_holdings)