from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from agents.analytics.sentiment import analyze_sentiment_finbert
from agents.voice.stt import transcribe_audio
from agents.llm.intent_classifier import classify_intent
from agents.llm.rag_pipeline import run_rag_pipeline
from agents.retriever.loader import load_and_chunk_mcp_data
from agents.retriever.embedder import embed_chunks
from agents.retriever.faiss_index import build_faiss_index
from agents.api.main import get_stock_data
from fastapi import Body
from agents.api.yfinance_client import (
    get_historical_stock_prices_yf,
    get_stock_info_yf,
    get_yahoo_finance_news_yf,
    get_stock_actions_yf,
    get_financial_statement_yf,
    get_holder_info_yf,
    get_option_expiration_dates_yf,
    get_option_chain_yf,
    get_recommendations_yf
)
from agents.voice.tts import speak_text

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "V.E.R.O.N.I.C.A backend is running."}

@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    transcript = transcribe_audio(audio_bytes)
    intent_result = classify_intent(transcript)

    tickers = intent_result.get("tickers", [])
    if isinstance(tickers, str):
        tickers = [tickers]
    intent_result["tickers"] = tickers

    return {
        "transcript": transcript,
        "intent": intent_result
    }

@app.post("/mcp/")
async def run_mcp_actions(request: Request):
    body = await request.json()
    intent_data = body.get("intent", {})

    intents = intent_data.get("intents", [])
    tickers = intent_data.get("tickers", [])
    if isinstance(tickers, str):
        tickers = [tickers]

    if not tickers:
        return {"error": "No ticker provided."}

    if len(tickers) > 1:
        return {
            "fallback_required": True,
            "tickers": tickers,
            "message": "Multiple tickers detected — fallback required."
        }

    ticker = tickers[0]

    time_frame = intent_data.get("time_frame", "1mo")
    region = intent_data.get("region", "")

    if not ticker:
        return {"error": "Ticker symbol is required."}

    result = {}

    result["news_summary"] = await get_yahoo_finance_news_yf(ticker)

    result["news_sentiment"] = []
    for article in result["news_summary"][:4]:
        if isinstance(article, dict):
            title = article.get("Title", "")
            summary = article.get("Summary", "")
            description = article.get("Description", "")
            text = f"{title}. {summary} {description}".strip()
        else:
            text = str(article)

        if text:
            sentiment = analyze_sentiment_finbert(text)
            result["news_sentiment"].append({
                "text": text,
                "sentiment": sentiment
            })

    for intent in intents:
        if intent == "stock_lookup":
            result["historical_prices"] = await get_historical_stock_prices_yf(ticker, time_frame)
            result["stock_info"] = await get_stock_info_yf(ticker)
            result["stock_actions"] = await get_stock_actions_yf(ticker)

        elif intent == "earnings_summary":
            result["financials"] = await get_financial_statement_yf(ticker, "income_stmt")
            result["recommendations"] = await get_recommendations_yf(ticker, "recommendations")

        elif intent == "sentiment_analysis":
            result["recommendations"] = await get_recommendations_yf(ticker, "upgrades_downgrades")

        elif intent == "risk_exposure":
            result["balance_sheet"] = await get_financial_statement_yf(ticker, "balance_sheet")
            result["cashflow"] = await get_financial_statement_yf(ticker, "cashflow")

        elif intent == "holder_analysis":
            result["institutional_holders"] = await get_holder_info_yf(ticker, "institutional_holders")
            result["insider_transactions"] = await get_holder_info_yf(ticker, "insider_transactions")

        elif intent == "option_insight":
            dates = await get_option_expiration_dates_yf(ticker)
            try:
                dates_list = eval(dates) if isinstance(dates, str) else dates
                first_date = dates_list[0] if dates_list else ""
                if first_date:
                    result["option_chain_calls"] = await get_option_chain_yf(ticker, first_date, "calls")
                    result["option_chain_puts"] = await get_option_chain_yf(ticker, first_date, "puts")
            except Exception as e:
                result["option_error"] = str(e)

        elif intent == "financials":
            result["income_stmt"] = await get_financial_statement_yf(ticker, "income_stmt")
            result["balance_sheet"] = await get_financial_statement_yf(ticker, "balance_sheet")
            result["cashflow"] = await get_financial_statement_yf(ticker, "cashflow")

        elif intent == "news_summary":
            pass

        else:
            result[f"{intent}_error"] = f"Unknown intent: {intent}"

    return {
        "ticker": ticker,
        "intents": intents,
        "data": result
    }

@app.post("/answer/")
async def answer(request: Request):
    body = await request.json()
    intent = body.get("intent", {})
    transcript = body.get("transcript", "")
    mcp_data = body.get("mcp_data", {})

    tickers = intent.get("tickers", [])
    if isinstance(tickers, str):
        tickers = [tickers]

    intents = intent.get("intents", [])

    if "unknown" in intents or len(tickers) > 1:
        from agents.fallback.fallback_summary import run_fallback_summary
        time_frame = intent.get("time_frame", "1mo")
        fallback_answer = await run_fallback_summary(tickers, time_frame)
        audio_path = speak_text(fallback_answer)

        return {
            "query": transcript,
            "answer": fallback_answer,
            "audio_path": audio_path,
            "mode": "fallback"
        }

    intent_type = intent.get("intent", "")
    time_frame = intent.get("time_frame", "")
    region = intent.get("region", "")

    if not mcp_data or not mcp_data.get("data"):
        return {
            "query": transcript,
            "answer": "MCP data missing — cannot run RAG pipeline."
        }    

    chunks = load_and_chunk_mcp_data(mcp_data)
    embedded = embed_chunks(chunks)
    build_faiss_index(embedded)

    query_parts = []
    if intent_type: query_parts.append(intent_type.replace("_", " "))
    if tickers:
        if len(tickers) == 1:
            query_parts.append(f"for {tickers[0]}")
        else:
            query_parts.append(f"for {', '.join(tickers)}")
    if time_frame: query_parts.append(f"in {time_frame}")
    if region: query_parts.append(f"({region})")

    query_string = " ".join(query_parts) or transcript

    mcp_data = body.get("mcp_data", {})
    metadata = {
        "tickers": tickers if isinstance(tickers, list) else [tickers],
        "region": region,
        "time_frame": time_frame,
        "intents": [intent_type],
        "mcp_data": mcp_data.get("data", {})
    }

    rag_answer = run_rag_pipeline(query_string, metadata=metadata)
    audio_path = "output_audio.wav"
    tts_path = speak_text(rag_answer)

    return {
        "query": query_string,
        "answer": rag_answer,
        "audio_path": tts_path
    }