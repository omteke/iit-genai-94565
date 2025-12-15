import streamlit as st
import login
import weather

if "page" not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page == "login":
    login.login_page()

elif st.session_state.page == "weather":
    weather.weather_page()
