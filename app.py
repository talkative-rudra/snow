import os
import time
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from google import genai
from gtts import gTTS
import speech_recognition as sr


try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


MODEL_NAME = "gemini-2.5-flash"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
STATIC_DIR = Path(__file__).with_name("static")
OUTPUT_FILE = STATIC_DIR / "snow_answer.mp3"
INPUT_AUDIO_FILE = STATIC_DIR / "voice_input.wav"


app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")


def normalize_prompt(prompt: str) -> str:
    return " ".join(prompt.lower().strip().replace("?", "").split())


def get_local_answer(user_prompt: str) -> str | None:
    prompt = normalize_prompt(user_prompt)
    now = datetime.now()

    identity_questions = {
        "who are you",
        "what are you",
        "who r u",
        "tell me about yourself",
        "introduce yourself",
        "what is your name",
        "your name",
    }
    greetings = {"hi", "hello", "hey", "yo", "sup", "good morning", "good afternoon", "good evening"}

    if prompt in identity_questions or "who are you" in prompt:
        return (
            "I'm SNOW, an AI voice assistant created by Rudi, trying to chat with you "
            "with the same humour that my boss has."
        )

    if prompt in greetings:
        return "Hey, I'm SNOW. What are we figuring out today?"

    if prompt in {"date", "today date", "what is the date", "what is today's date"}:
        return f"Today is {now.strftime('%A, %B %d, %Y')}."

    if prompt in {"time", "current time", "what is the time", "what time is it"}:
        return f"The current time is {now.strftime('%I:%M %p')}."

    if prompt in {"day", "what day is it", "which day is it"}:
        return f"It's {now.strftime('%A')} today."

    return None


def build_prompt(user_prompt: str) -> str:
    return f"""
You are SNOW, a friendly voice assistant.

Answer the user's prompt in a natural, human, spoken style.
Keep the response brief and audio-friendly by default: usually 1 to 3 short sentences.
Use light humor only when it fits naturally. Do not force jokes.
Avoid long lists, markdown formatting, headings, and overly formal explanations.
If the user explicitly asks to explain, describe, elaborate, compare in detail, or give steps,
then give a clearer longer answer, but still keep it conversational.

User prompt: {user_prompt}
""".strip()


def ask_snow(user_prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("Set GEMINI_API_KEY before starting the server.")

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=build_prompt(user_prompt),
    )

    answer = response.text.strip() if response.text else ""
    if not answer:
        raise RuntimeError("SNOW returned an empty response.")

    return answer


def save_audio(answer: str) -> str:
    STATIC_DIR.mkdir(exist_ok=True)
    gTTS(text=answer, lang="en").save(str(OUTPUT_FILE))
    return f"/static/{OUTPUT_FILE.name}?v={int(time.time() * 1000)}"


def transcribe_audio(audio_file: Path) -> str:
    recognizer = sr.Recognizer()
    with sr.AudioFile(str(audio_file)) as source:
        audio = recognizer.record(source)

    return recognizer.recognize_google(audio).strip()


@app.get("/")
def index():
    return send_from_directory(".", "index.html")


@app.post("/api/ask")
def ask():
    data = request.get_json(silent=True) or {}
    prompt = str(data.get("prompt", "")).strip()
    voice_enabled = bool(data.get("voice_enabled", True))

    if not prompt:
        return jsonify({"error": "Prompt cannot be empty."}), 400

    try:
        answer = get_local_answer(prompt) or ask_snow(prompt)
        audio_url = save_audio(answer) if voice_enabled else None
        return jsonify({"answer": answer, "audio_url": audio_url, "voice_enabled": voice_enabled})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.post("/api/transcribe")
def transcribe():
    audio = request.files.get("audio")
    if audio is None:
        return jsonify({"error": "No audio file was received."}), 400

    input_audio_file = STATIC_DIR / f"voice_input_{time.time_ns()}.wav"

    try:
        STATIC_DIR.mkdir(exist_ok=True)
        audio.save(input_audio_file)
        transcript = transcribe_audio(input_audio_file)
        return jsonify({"transcript": transcript})
    except sr.UnknownValueError:
        return jsonify({"error": "I could not understand the audio. Try speaking closer to the mic."}), 400
    except sr.RequestError as exc:
        return jsonify({"error": f"Speech-to-text service failed: {exc}"}), 500
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    finally:
        input_audio_file.unlink(missing_ok=True)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
