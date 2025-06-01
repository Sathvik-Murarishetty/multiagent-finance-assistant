# 🎙️ Market Analyst AI — Voice-Enabled Financial Assistant

**Markel Analyst AI** (Voice-Enabled Retrieval-Optimized Natural Intelligence for Capital Analysis) is a multi-agent, voice-based financial assistant that provides smart, spoken market briefings based on real-time data and structured document retrieval.

🔗 [Live Frontend (Streamlit)](https://veronica-streamlit-frontend.onrender.com)

---

## Features

- Voice-input query system using Streamlit audio recorder
- Intent classification and entity detection (tickers, actions, timeframes)
- Live market data via `yfinance`, option chains, earnings, holders, financials
- Real-time news scraping using `beautifulsoup4`
- Retrieval-Augmented Generation (RAG) for LLM-powered insights
- Model Context Protocol (MCP) for multi-agent structured data ingestion
- Audio response using `gTTS` and `pydub`
- Carousel UX for news while backend runs

---

## How RAG is Implemented

The Model uses a **Retrieval-Augmented Generation** pipeline for deep financial analysis:

1. **Audio Transcription**: Whisper-based transcription converts user voice into text.
2. **Intent Classification**: The query is analyzed to extract:
   - `intent`: e.g. `stock_lookup`, `earnings_summary`, `risk_exposure`
   - `ticker(s)`, `time_frame`, and other metadata
3. **Data Retrieval (via MCP)**:
   - Custom MCP agents retrieve structured financial data:
     - Stock price, EPS, financials (`yfinance`)
     - Option chains, sentiment scores, holders
     - News articles using scraping
4. **Prompt Construction**: Injected into a system prompt:
   
   ```text
   User Query:
   "Compare Nvidia and AMD for the past 3 months."

   Context:
   {"intent": "compare", "tickers": ["NVDA", "AMD"], "time_frame": "3 months"}

   Retrieved Data:
   - EPS NVDA: 1.75 vs 1.52 expected
   - EPS AMD: 0.74 vs 0.80 expected
   - Sentiment: Mixed for NVDA, Neutral for AMD
   ```

5. **LLM Response Generation**:

   * LLM (via OpenRouter & Mistral) generates a well-structured, <250 word insight.
6. **TTS Output**: Answer is converted to spoken audio and auto-played.

---

## MCP Usage

**MCP (Model Context Protocol)** is a coordination layer that lets agents fetch, structure, and bundle context for RAG.
Each intent maps to one or more agent fetchers like:

| Intent              | MCP Agents Used                         |
| ------------------- | --------------------------------------- |
| stock\_lookup       | `stock_price`, `market_cap`, `summary`  |
| earnings\_summary   | `eps`, `surprise`, `quarter_data`       |
| sentiment\_analysis | `finbert_api`, `news_summary`           |
| risk\_exposure      | `aum`, `pca`, `volatility_index`        |
| holder\_analysis    | `top_holders`, `ownership_distribution` |
| option\_insight     | `open_interest`, `volume`, `strikes`    |

MCP ensures modular, extensible agent-based data pipelines.

---

## How to Run Locally

### Backend (FastAPI)

```bash
git clone https://github.com/Sathvik-Murarishetty/multiagent-finance-assistant
pip install -r requirements.txt
uvicorn orchestrator.main:app --reload --port 8000
```

### Frontend (Sreamlit)

```bash
streamlit run streamlit_app/app.py
```

---

## Tech Stack

| Layer      | Tools Used                                       |
| ---------- | ------------------------------------------------ |
| Frontend   | Streamlit, HTML, CSS                             |
| Backend    | FastAPI, Uvicorn                                 |
| Audio      | `faster-whisper`, `gTTS`, `pydub`                |
| RAG        | `transformers`, `sentence-transformers`, `faiss` |
| Finance    | `yfinance`, `beautifulsoup4`, `lxml`             |
| AI API     | Mistral via OpenRouter, FinBERT via HuggingFace  |
| Deployment | Render (Streamlit + FastAPI)                     |

---

## ⚠️ Note on Performance

> **The Model usually responds in under 5 seconds.**
> However, due to **free-tier cloud limitations** (CPU & memory), response time may increase slightly.
> **Hang on tight!** It’s still worth it.

---

## Maintainer

> **Sathvik Murarishetty**
> MIT Bengaluru · Computer Science (2025)
> [LinkedIn](https://www.linkedin.com/in/sathvikmurarishetty) • [GitHub](https://github.com/Sathvik-Murarishetty)

---

## Sample Prompts

* “What is Nike's stock price today, and should I invest in it?”
* “Summarize Apple's earnings and news highlights.”
* “What's the sentiment around Tesla this month?”
* “Compare Intel and AMD for the past 3 months.”
* “Show Google's risk analysis and key shareholders.”
* “What is Microsoft's option chain insight?”
