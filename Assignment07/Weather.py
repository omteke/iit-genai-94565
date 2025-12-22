from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
import requests
import streamlit as st

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
openweather_api_key = os.getenv("OPENWEATHER_API_KEY")


llm = init_chat_model(
    model="llama-3.3-70b-versatile",
    model_provider="openai",
    base_url="https://api.groq.com/openai/v1",
    api_key=groq_api_key
)

st.title("Weather ChatBot")

conversation = [
    {"role": "system", "content": "You are a weather analyst with 10 years of experience. Explain weather clearly."}
]


city = st.chat_input("Enter city: ")

# Weather API call
weather_url = (
    f"https://api.openweathermap.org/data/2.5/weather"
    f"?q={city}&appid={openweather_api_key}&units=metric"
)

response = requests.get(weather_url)
st.write("Status:", response.status_code)

if response.status_code != 200:
    st.write("Error fetching weather:", response.json())
    exit()

weather = response.json()


weather_prompt = f"""
City: {city}
Temperature: {weather['main']['temp']} °C
Humidity: {weather['main']['humidity']} %
Wind speed: {weather['wind']['speed']} m/s
Condition: {weather['weather'][0]['description']}

Explain this weather in simple English.
"""

# Call LLM
result = llm.invoke(
    conversation + [{"role": "user", "content": weather_prompt}]
)

st.subheader("\n🌦 Weather Information:")
st.write(f"weather status of {city}:")
st.write(result.content)
