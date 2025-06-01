import streamlit as st
from audio_recorder_streamlit import audio_recorder
import requests, base64, time, threading
import os
from dotenv import load_dotenv

load_dotenv()

FASTAPI_HOST = os.getenv("FASTAPI_HOST")
TRANSCRIBE_URL = f"{FASTAPI_HOST}/transcribe/"
MCP_URL        = f"{FASTAPI_HOST}/mcp/"
ANSWER_URL     = f"{FASTAPI_HOST}/answer/"

st.set_page_config(page_title="V.E.R.O.N.I.C.A", page_icon="🎙️", layout="centered")
st.title("🎙️ V.E.R.O.N.I.C.A")
st.caption("Your Voice-Based Financial Assistant")

def autoplay_audio(path: str):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <audio controls autoplay>
          <source src="data:audio/wav;base64,{b64}" type="audio/wav">
        </audio>""",
        unsafe_allow_html=True,
    )

def headline_html(ticker: str, art: dict) -> str:
    title   = art.get("Title",   "No Title")
    summary = art.get("Summary", "No Summary")
    url     = art.get("URL",     "#")
    return f"""
    <h4 style="margin:0 0 6px 0;">What’s making headlines…</h4>
    <div style="padding:10px;border:1px solid #e1e1e1;border-radius:6px;">
      <strong>{ticker} in the news:</strong><br>
      <span style="color:#f39c12;font-size:18px;">{title}</span><br>
      <span style="font-size:14px;">{summary}</span><br>
      <a href="{url}" target="_blank">Read full article ↗︎</a>
    </div>
    """

st.markdown("### Record Your Query")
audio_bytes = audio_recorder(
    text="",
    recording_color="#e8b62c",
    neutral_color="#6aa36f",
    icon_name="microphone-lines",
    icon_size="2x",
)

if audio_bytes:
    st.markdown("Recording complete!")
    st.audio(audio_bytes, format="audio/wav")

    st.markdown("### Transcribe & Understand Your Query")
    with st.spinner("Transcribing and classifying intent…"):
        tr = requests.post(
            TRANSCRIBE_URL,
            files={"file": ("audio.wav", audio_bytes, "audio/wav")},
        )
    if tr.status_code != 200:
        st.error("Failed to get transcript and intent."); st.stop()

    data        = tr.json()
    transcript  = data.get("transcript", "")
    intent      = data.get("intent", {})
    ticker_name = intent.get("ticker", "This stock").upper()

    tabs = st.tabs(["Transcript", "Intent"])
    with tabs[0]:
        st.markdown(f"**You said:**\n> {transcript}")
    with tabs[1]:
        st.json(intent)

    st.markdown("### Fetching Structured Market Data")
    with st.spinner("Calling MCP agent…"):
        mcp_r = requests.post(MCP_URL, json={"transcript": transcript, "intent": intent})
    if mcp_r.status_code != 200:
        st.warning("Failed to retrieve MCP output."); st.stop()

    mcp_data = mcp_r.json()
    st.markdown("MCP Data Retrieved Successfully")
    with st.expander("View Raw MCP Data"):
        st.json(mcp_data)

    st.markdown("### Generating Final Answer")
    carousel_box = st.empty()
    answer_box   = st.empty()

    done_evt   = threading.Event()
    answer_res = {}

    def fetch_answer():
        global answer_res
        try:
            resp = requests.post(
                ANSWER_URL,
                json={"transcript": transcript, "intent": intent, "mcp_data": mcp_data},
                timeout=None,
            )
            if resp.status_code == 200:
                answer_res = resp.json()
        finally:
            done_evt.set()

    threading.Thread(target=fetch_answer, daemon=True).start()

    articles = mcp_data.get("data", {}).get("news_summary", [])
    idx = 0
    while not done_evt.is_set():
        if articles:
            carousel_box.markdown(
                headline_html(ticker_name, articles[idx % len(articles)]),
                unsafe_allow_html=True,
            )
            idx += 1
        time.sleep(7)

    carousel_box.empty()

    answer_text = answer_res.get("answer", "No answer returned.")
    audio_path  = answer_res.get("audio_path", "")

    answer_box.markdown("## V.E.R.O.N.I.C.A's Answer")
    answer_box.markdown(answer_text)
    if audio_path:
        autoplay_audio(audio_path)
    else:
        st.warning("No audio response available.")

    st.toast("Response generated — scroll down to view it", icon=None)
