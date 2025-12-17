import requests
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GROQ_API_KEY or not GEMINI_API_KEY:
    raise ValueError("API keys are missing")

# Get user input
user_input = input("Ask me anything: ").strip()
if not user_input:
    print("Input cannot be empty.")
    exit()

print("\nSending same prompt to Gemini and Groq...\n")

# =========================
# GEMINI API CALL
# =========================
gemini_url = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent?key=" + GEMINI_API_KEY
)

gemini_payload = {
    "contents": [
        {
            "parts": [{"text": user_input}]
        }
    ],
    "generationConfig": {
        "temperature": 0.7,
        "maxOutputTokens": 512
    }
}

start_time = time.time()
gemini_response = requests.post(
    gemini_url,
    headers={"Content-Type": "application/json"},
    json=gemini_payload,
    timeout=30
)
gemini_time = time.time() - start_time

# =========================
# GROQ API CALL
# =========================
groq_url = "https://api.groq.com/openai/v1/chat/completions"

groq_headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

groq_payload = {
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {"role": "user", "content": user_input}
    ]
}

start_time = time.time()
groq_response = requests.post(
    groq_url,
    headers=groq_headers,
    json=groq_payload,
    timeout=30
)
groq_time = time.time() - start_time

# =========================
# OUTPUT
# =========================

print("========== GEMINI RESPONSE ==========")
if gemini_response.status_code == 200:
    try:
        gemini_text = gemini_response.json()["candidates"][0]["content"]["parts"][0]["text"]
        print(gemini_text)
    except Exception:
        print("Failed to parse Gemini response")
else:
    print("Gemini Error:", gemini_response.text)

print("\n========== GROQ RESPONSE ==========")
if groq_response.status_code == 200:
    try:
        groq_text = groq_response.json()["choices"][0]["message"]["content"]
        print(groq_text)
    except Exception:
        print("Failed to parse Groq response")
else:
    print("Groq Error:", groq_response.text)

# =========================
# SPEED COMPARISON
# =========================
print("\n========== SPEED COMPARISON ==========")
print(f"Gemini Response Time: {gemini_time:.2f} seconds")
print(f"Groq Response Time  : {groq_time:.2f} seconds")

if gemini_time < groq_time:
    print("⚡ Gemini is faster")
else:
    print("⚡ Groq is faster")