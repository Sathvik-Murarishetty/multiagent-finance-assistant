from faster_whisper import WhisperModel
import tempfile
import os

model = WhisperModel("base", device="cpu", compute_type="int8")  # use "tiny" if resources are low

def transcribe_audio(audio_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio_bytes)
        temp_path = temp_audio.name

    try:
        segments, _ = model.transcribe(temp_path)
        transcript = " ".join([segment.text for segment in segments])
    except Exception as e:
        transcript = f"Transcription failed: {e}"
    finally:
        os.remove(temp_path)

    return transcript
