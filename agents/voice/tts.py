from gtts import gTTS
from pydub import AudioSegment
import os
import tempfile

def speak_text(text: str, speed: float = 1.2) -> str:
    """
    Generate TTS audio using gTTS and speed it up using pydub.

    Takes Args: Text to convert and Speed multiplier
    Returns: Path to the final audio file (WAV).
    """
    try:
        temp_dir = tempfile.gettempdir()
        mp3_path = os.path.join(temp_dir, "veronica_tts.mp3")
        wav_path = os.path.join(temp_dir, "veronica_tts_final.wav")

        tts = gTTS(text, lang="en", slow=False)
        tts.save(mp3_path)

        sound = AudioSegment.from_file(mp3_path)
        new_sound = sound._spawn(sound.raw_data, overrides={
            "frame_rate": int(sound.frame_rate * speed)
        }).set_frame_rate(sound.frame_rate)

        new_sound.export(wav_path, format="wav")
        return wav_path

    except Exception as e:
        print(f"TTS generation failed: {e}")
        return ""