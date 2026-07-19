# SNOW Voice Assistant

SNOW is a local Flask-based voice assistant UI with typed prompts, microphone input, Gemini responses, text-to-speech output, chat history, and speaker mute support.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file or set the environment variable:

```powershell
$env:GEMINI_API_KEY="your_gemini_api_key_here"
```

Run the app:

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:5000/
```

## Notes

- Do not commit `.env` or API keys.
- Generated audio files are ignored by Git.
- Microphone access works best in Chrome or Edge.
