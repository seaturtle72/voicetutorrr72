
from flask import Flask, request, jsonify, send_file
import requests
import os
import uuid

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

@app.route("/")
def home():
    return send_file("static/index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_text = request.json.get("question", "")

    # Step 1: Get response from OpenRouter (LLaMA)
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "meta-llama/llama-3-8b-instruct",
            "messages": [{"role": "user", "content": user_text}]
        }
    )
    response_json = response.json()
    ai_reply = response_json["choices"][0]["message"]["content"]

    # Step 2: Generate speech with ElevenLabs
    audio_response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "text": ai_reply,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.7
            }
        }
    )

    filename = f"static/audio_{uuid.uuid4().hex}.mp3"
    with open(filename, "wb") as f:
        f.write(audio_response.content)

    return jsonify({"audio_url": f"/{filename}"})
