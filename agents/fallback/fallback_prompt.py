from agents.llm.rag_pipeline import query_llm

def build_multi_ticker_fallback_prompt(query: str, metadata: dict) -> str:
    tickers = metadata.get("tickers", [])
    time_frame = metadata.get("time_frame", "")
    mcp_data = metadata.get("mcp_data", {})

    comparison_info = ""

    for ticker in tickers:
        data = mcp_data.get(ticker, {})
        if data.get("error"):
            comparison_info += f"\nData error for {ticker}: {data['error']}\n"
            continue

        stock_info = data.get("stock_info", {}) if isinstance(data.get("stock_info"), dict) else {}
        prices = data.get("historical_prices", []) if isinstance(data.get("historical_prices"), list) else []
        financials = data.get("financials", [])
        if isinstance(financials, list) and financials and isinstance(financials[0], dict):
            revenue = financials[0].get("Total Revenue", "N/A")
            eps = financials[0].get("EPS", "N/A")
        else:
            revenue = "N/A"
            eps = "N/A"

        price_summary = prices[-1] if prices and isinstance(prices[-1], dict) else {}
        current_price = price_summary.get("close", "N/A")
        name = stock_info.get("shortName", ticker)

        comparison_info += f"""
Company: {name} ({ticker})
- Current Price: {current_price}
- Revenue: {revenue}
- EPS: {eps}
---
"""

    prompt = f"""
You are VERONICA, a professional financial assistant.

Using the structured financial data below, generate a 250-word comparative analysis of the companies mentioned. Your tone should be analytical yet approachable. Use company names instead of tickers when referring to them. Include stock price trends, revenue, and EPS insights. End with a one-line concluding thought.

User Query:
"{query}"

Time Frame: {time_frame}

Data Summary:
{comparison_info}

Now write the 250-word comparative financial brief.
""".strip()

    return prompt