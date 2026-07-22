# SNOW Voice Assistant

SNOW is a dark-themed AI voice assistant built with Flask, Gemini, browser microphone input, speech-to-text, and text-to-speech audio output. It supports both typed and spoken prompts, keeps a lightweight chat history in the browser, and can answer simple local questions without calling the AI model.

## Features

- Modern responsive web UI for desktop, laptop, tablet, and mobile
- Typed prompt input with Enter-to-send support
- Click-to-talk microphone flow
- Live browser-side speech preview with final server-side transcription
- Gemini-powered answers using `gemini-3.1-flash-lite`
- Local answers for common prompts like time, date, greetings, and identity
- Text-to-speech output using gTTS
- Speaker mute/unmute that persists across messages
- Browser chat history using `localStorage`
- Render-ready Flask backend

## Tech Stack

- Python
- Flask
- Google Gemini API
- gTTS
- SpeechRecognition
- HTML, CSS, and JavaScript
- Gunicorn for production hosting

## Project Structure

```text
.
+-- app.py              # Flask backend and API routes
+-- index.html          # Main SNOW web UI
+-- requirements.txt    # Python dependencies
+-- .env.example        # Example environment variable file
+-- .gitignore          # Files ignored by Git
+-- README.md           # Project documentation
```

## Local Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Run the app:

```powershell
python app.py
```

Open the app:

```text
http://127.0.0.1:5000/
```



## Notes

- Microphone access works best in Chrome or Edge.
- On hosted deployments, the browser may require HTTPS for microphone permissions.
- Generated audio files are temporary runtime output and should not be committed.

