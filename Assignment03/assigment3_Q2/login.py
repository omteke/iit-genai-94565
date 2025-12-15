import streamlit as st

def login_page():
    st.title("Login to Weather App")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("LOGIN", type="primary"):   
        if username == "om" and password == "1234":
            st.session_state.page = "weather"  
            st.success("Login successful!")
            st.rerun()                         
        else:
            st.error("Invalid username or password")
