import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ---------------- FILE PATHS ----------------
USERS_FILE = "users.csv"
HISTORY_FILE = "userfiles.csv"

# ---------------- CREATE CSV FILES IF NOT EXIST ----------------
if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["userid", "password"]).to_csv(USERS_FILE, index=False)

if not os.path.exists(HISTORY_FILE):
    pd.DataFrame(columns=["userid", "filename", "datetime"]).to_csv(HISTORY_FILE, index=False)

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- REGISTER ----------------
def register():
    st.subheader("Register")

    userid = st.text_input("User ID").strip()
    password = st.text_input("Password", type="password").strip()

    if st.button("Register"):
        if userid == "" or password == "":
            st.error("Fields cannot be empty")
            return

        users = pd.read_csv(USERS_FILE, dtype=str)

        if userid in users["userid"].values:
            st.error("User already exists")
        else:
            new_user = pd.DataFrame(
                [[userid, password]],
                columns=["userid", "password"]
            )
            users = pd.concat([users, new_user], ignore_index=True)
            users.to_csv(USERS_FILE, index=False)
            st.success("Registration successful. Please login.")

# ---------------- LOGIN ----------------
def login():
    st.subheader("Login")

    userid = st.text_input("User ID").strip()
    password = st.text_input("Password", type="password").strip()

    if st.button("Login"):
        users = pd.read_csv(USERS_FILE, dtype=str)

        match = users[
            (users["userid"].str.strip() == userid) &
            (users["password"].str.strip() == password)
        ]

        if not match.empty:
            st.session_state.logged_in = True
            st.session_state.user = userid
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

# ---------------- CSV UPLOAD ----------------
def explore_csv():
    st.subheader("Explore CSV")

    file = st.file_uploader("Upload a CSV file", type=["csv"])

    if file is not None:
        df = pd.read_csv(file)
        st.dataframe(df)

        history = pd.read_csv(HISTORY_FILE)
        new_entry = pd.DataFrame(
            [[st.session_state.user, file.name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]],
            columns=["userid", "filename", "datetime"]
        )

        history = pd.concat([history, new_entry], ignore_index=True)
        history.to_csv(HISTORY_FILE, index=False)

        st.success("Upload history saved")

# ---------------- VIEW HISTORY ----------------
def view_history():
    st.subheader("Upload History")

    history = pd.read_csv(HISTORY_FILE)
    user_history = history[history["userid"] == st.session_state.user]

    if user_history.empty:
        st.info("No uploads yet")
    else:
        st.dataframe(user_history)

# ---------------- SIDEBAR MENU ----------------
st.sidebar.title("Menu")

if not st.session_state.logged_in:
    menu = st.sidebar.selectbox("Select", ["Home", "Login", "Register"])

    if menu == "Home":
        st.title("Welcome")
        st.write("Please login or register to continue.")

    elif menu == "Login":
        login()

    elif menu == "Register":
        register()

else:
    menu = st.sidebar.selectbox("Select", ["Explore CSV", "See History", "Logout"])

    if menu == "Explore CSV":
        explore_csv()

    elif menu == "See History":
        view_history()

    elif menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.user = None
        st.success("Logged out successfully")
        st.rerun()
