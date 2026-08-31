import yfinance as yf

def get_price_history(ticker: str, period: str = "3mo"):
    """
    Fetch OHLC price history for an NSE stock.
    ticker: plain ticker like 'TCS' (NSE .NS suffix added automatically)
    period: how far back, e.g. '1mo', '3mo', '6mo', '1y'
    """
    nse_ticker = f"{ticker.upper()}.NS"
    stock = yf.Ticker(nse_ticker)
    hist = stock.history(period=period)

    if hist.empty:
        return None

    data = []
    for date, row in hist.iterrows():
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "open": round(row["Open"], 2),
            "high": round(row["High"], 2),
            "low": round(row["Low"], 2),
            "close": round(row["Close"], 2),
            "volume": int(row["Volume"]),
        })
    return data


if __name__ == "__main__":
    result = get_price_history("TCS")
    if result:
        print(f"Got {len(result)} days of data. Most recent:")
        print(result[-1])
    else:
        print("No data returned — check ticker or internet connection.")