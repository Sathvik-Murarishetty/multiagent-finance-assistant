from agents.api.yfinance_client import (
    get_stock_info_yf,
    get_historical_stock_prices_yf,
    get_financial_statement_yf,
)
from .fallback_prompt import build_multi_ticker_fallback_prompt
from agents.llm.rag_pipeline import query_llm


async def run_fallback_summary(tickers: list, time_frame: str = "1mo") -> str:
    combined_data = {}

    for ticker in tickers:
        try:
            stock_info = await get_stock_info_yf(ticker)
            prices = await get_historical_stock_prices_yf(ticker, time_frame)
            financials = await get_financial_statement_yf(ticker, "income_stmt")

            combined_data[ticker] = {
                "stock_info": stock_info,
                "historical_prices": prices,
                "financials": financials,
            }

        except Exception as e:
            combined_data[ticker] = {
                "error": str(e)
            }

    metadata = {
        "tickers": tickers,
        "time_frame": time_frame,
        "intents": ["stock_lookup", "financials"],
        "mcp_data": combined_data,
    }

    query = f"Compare {' and '.join(tickers)} over the last {time_frame}."
    prompt = build_multi_ticker_fallback_prompt(query, metadata)
    return query_llm(prompt)