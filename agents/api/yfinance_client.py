import json
from enum import Enum
import pandas as pd
import yfinance as yf
from utils.timeframe_parser import parse_natural_timeframe

class FinancialType(str, Enum):
    income_stmt = "income_stmt"
    quarterly_income_stmt = "quarterly_income_stmt"
    balance_sheet = "balance_sheet"
    quarterly_balance_sheet = "quarterly_balance_sheet"
    cashflow = "cashflow"
    quarterly_cashflow = "quarterly_cashflow"

class HolderType(str, Enum):
    major_holders = "major_holders"
    institutional_holders = "institutional_holders"
    mutualfund_holders = "mutualfund_holders"
    insider_transactions = "insider_transactions"
    insider_purchases = "insider_purchases"
    insider_roster_holders = "insider_roster_holders"

class RecommendationType(str, Enum):
    recommendations = "recommendations"
    upgrades_downgrades = "upgrades_downgrades"

async def get_historical_stock_prices_yf(ticker: str, user_input_time: str = "1mo", interval: str = "1d") -> dict:
    period = parse_natural_timeframe(user_input_time)
    company = yf.Ticker(ticker)

    try:
        if company.isin is None:
            return {"error": f"Company ticker '{ticker}' not found."}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}

    try:
        hist_data = company.history(period=period, interval=interval)
        hist_data = hist_data.reset_index(names="Date")
        return json.loads(hist_data.to_json(orient="records", date_format="iso"))
    except Exception as e:
        return {"error": f"Failed to fetch or format historical data: {str(e)}"}

async def get_stock_info_yf(ticker: str) -> str:
    """
    Get stock information for a given ticker symbol.

    Takes Args: ticker (str)
    Returns: JSON string with stock details or error
    """
    company = yf.Ticker(ticker)
    try:
        if company.isin is None:
            return f"Company ticker {ticker} not found."
    except Exception as e:
        return f"Error: getting stock information for {ticker}: {e}"

    info = company.info
    return json.dumps(info)

async def get_yahoo_finance_news_yf(ticker: str) -> list:
    """
    Get latest Yahoo Finance news for a ticker
    """
    company = yf.Ticker(ticker)
    try:
        if company.isin is None:
            return []
    except Exception:
        return []

    try:
        news_data = company.news
    except Exception:
        return []

    news_list = []
    for news in news_data:
        content = news.get("content", {})
        if content.get("contentType", "") == "STORY":
            news_list.append({
                "Title": content.get("title", ""),
                "Summary": content.get("summary", ""),
                "Description": content.get("description", ""),
                "URL": content.get("canonicalUrl", {}).get("url", "")
            })

    return news_list

async def get_stock_actions_yf(ticker: str) -> str:
    """
    Get stock dividends and stock splits for a given ticker.

    Takes Args: ticker - Stock symbol
    Returns: JSON string of stock action records
    """
    try:
        company = yf.Ticker(ticker)
        actions_df = company.actions
        actions_df = actions_df.reset_index(names="Date")
        return actions_df.to_json(orient="records", date_format="iso")
    except Exception as e:
        return f"Error: getting stock actions for {ticker}: {e}"

async def get_financial_statement_yf(ticker: str, financial_type: str) -> str:
    """
    Get financial statement for a given ticker.

    Takes Args: ticker and financial_type (One of the predefined FinancialType values)
    Returns: JSON of financial data by date
    """
    try:
        company = yf.Ticker(ticker)
        if company.isin is None:
            return f"Error: Company ticker {ticker} not found."
    except Exception as e:
        return f"Error: getting financial statement for {ticker}: {e}"

    match financial_type:
        case "income_stmt":
            data = company.income_stmt
        case "quarterly_income_stmt":
            data = company.quarterly_income_stmt
        case "balance_sheet":
            data = company.balance_sheet
        case "quarterly_balance_sheet":
            data = company.quarterly_balance_sheet
        case "cashflow":
            data = company.cashflow
        case "quarterly_cashflow":
            data = company.quarterly_cashflow
        case _:
            return f"Error: Invalid financial_type `{financial_type}`"

    result = []
    for col in data.columns:
        date_str = col.strftime("%Y-%m-%d") if isinstance(col, pd.Timestamp) else str(col)
        entry = {"date": date_str}
        for metric, value in data[col].items():
            entry[metric] = None if pd.isna(value) else value
        result.append(entry)

    return json.dumps(result)

async def get_holder_info_yf(ticker: str, holder_type: str) -> str:
    """
    Get holder information (insiders, institutions, mutual funds) for a ticker

    Takes Args: ticker and holder_type (One of the predefined HolderType values)
    Returns: JSON representation of holder data
    """
    try:
        company = yf.Ticker(ticker)
        if company.isin is None:
            return f"Error: Company ticker {ticker} not found."
    except Exception as e:
        return f"Error: getting holder info for {ticker}: {e}"

    try:
        match holder_type:
            case "major_holders":
                df = company.major_holders.reset_index(names="metric")
            case "institutional_holders":
                df = company.institutional_holders
            case "mutualfund_holders":
                df = company.mutualfund_holders
            case "insider_transactions":
                df = company.insider_transactions
            case "insider_purchases":
                df = company.insider_purchases
            case "insider_roster_holders":
                df = company.insider_roster_holders
            case _:
                return f"Error: Invalid holder type `{holder_type}`"
        
        return df.to_json(orient="records", date_format="iso")
    except Exception as e:
        return f"Error: Failed to fetch {holder_type} for {ticker}: {e}"

async def get_option_expiration_dates_yf(ticker: str) -> str:
    """
    Fetch available options expiration dates for a given ticker symbol

    Takes Args: ticker
    Returns: JSON array of expiration dates or error message
    """
    try:
        company = yf.Ticker(ticker)
        if company.isin is None:
            return f"Error: Company ticker {ticker} not found."
    except Exception as e:
        return f"Error: getting option expiration dates for {ticker}: {e}"

    try:
        return json.dumps(company.options)
    except Exception as e:
        return f"Error: failed to fetch options data for {ticker}: {e}"

async def get_option_chain_yf(ticker: str, expiration_date: str, option_type: str) -> str:
    """
    Fetch option chain for given ticker, expiration date, and option type

    Takes Args: ticker, expiration_date and option_type
    Returns: JSON string containing the option chain data or error
    """
    try:
        company = yf.Ticker(ticker)
        if company.isin is None:
            return f"Error: Company ticker {ticker} not found."
    except Exception as e:
        return f"Error: creating Ticker object for {ticker}: {e}"

    if expiration_date not in company.options:
        return f"Error: No options available for date {expiration_date}. Try get_option_expiration_dates."

    if option_type not in ["calls", "puts"]:
        return "Error: Invalid option type. Use 'calls' or 'puts'."

    try:
        chain = company.option_chain(expiration_date)
        if option_type == "calls":
            return chain.calls.to_json(orient="records", date_format="iso")
        else:
            return chain.puts.to_json(orient="records", date_format="iso")
    except Exception as e:
        return f"Error: getting option chain for {ticker}: {e}"

async def get_recommendations_yf(ticker: str, recommendation_type: str, months_back: int = 12) -> str:
    """
    Get analyst recommendations or upgrades/downgrades for a given ticker symbol.

    Takes Args: ticker, recommendation_type and months_back
    Returns: JSON of relevant recommendations
    """
    try:
        company = yf.Ticker(ticker)
        if company.isin is None:
            return f"Error: Company ticker {ticker} not found."
    except Exception as e:
        return f"Error: creating Ticker object for {ticker}: {e}"

    try:
        if recommendation_type == "recommendations":
            return company.recommendations.to_json(orient="records")

        elif recommendation_type == "upgrades_downgrades":
            df = company.upgrades_downgrades.reset_index()
            cutoff = pd.Timestamp.now() - pd.DateOffset(months=months_back)
            df = df[df["GradeDate"] >= cutoff].sort_values("GradeDate", ascending=False)
            latest = df.drop_duplicates(subset=["Firm"])
            return latest.to_json(orient="records", date_format="iso")

        else:
            return "Error: Invalid recommendation_type. Use 'recommendations' or 'upgrades_downgrades'."

    except Exception as e:
        return f"Error: retrieving recommendations for {ticker}: {e}"