import requests
import os
from dotenv import load_dotenv
import streamlit as st

def weather_page():   
    load_dotenv()
    api_key = os.getenv("OPENWEATHER_API_KEY")

    st.title("🌦 Weather App")

    if st.button("Logout"):
        st.session_state.page = "login"
        st.rerun()

    city = st.text_input("Enter city")

    if city:
        url = f"https://api.openweathermap.org/data/2.5/weather?appid={api_key}&units=metric&q={city}"
        response = requests.get(url)
        data = response.json()

        if data.get("cod") == 200:
            st.subheader(f"Weather in {city}")
            st.write("🌡 Temperature:", data["main"]["temp"], "°C")
            st.write("💧 Humidity:", data["main"]["humidity"])
            st.write("🌬 Wind Speed:", data["wind"]["speed"])
            st.write("☁ Description:", data["weather"][0]["description"])
        else:
            st.error("Invalid city name")
