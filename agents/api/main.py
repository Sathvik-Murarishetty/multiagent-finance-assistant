import yfinance as yf
from datetime import datetime, timedelta

def get_date_range(time_frame: str):
    """
    Returns start and end dates based on time_frame input
    """
    today = datetime.today()

    if time_frame.lower() == "today":
        return today.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
    elif time_frame.lower() == "this week":
        start = today - timedelta(days=today.weekday())
        return start.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
    elif time_frame.lower() == "this month":
        start = today.replace(day=1)
        return start.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
    else:
        return None, None

def get_stock_data(ticker: str, time_frame: str = "today") -> dict:
    """
    Fetches stock price data for a given ticker and time frame
    """
    start, end = get_date_range(time_frame)
    if not start or not end:
        return {"error": f"Unsupported time_frame: {time_frame}"}

    try:
        df = yf.download(ticker, start=start, end=end)
        if df.empty:
            return {"error": "No data available for the given time frame"}

        latest = df.iloc[-1]
        return {
            "ticker": ticker.upper(),
            "date": latest.name.strftime("%Y-%m-%d"),
            "open": latest["Open"],
            "close": latest["Close"],
            "high": latest["High"],
            "low": latest["Low"],
            "volume": int(latest["Volume"])
        }

    except Exception as e:
        return {"error": str(e)}