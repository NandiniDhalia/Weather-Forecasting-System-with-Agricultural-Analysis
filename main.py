import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import extra_streamlit_components as stx
from datetime import datetime, timedelta

from auth_page import show_auth_page
from guest_page import view_guest_page
from database import initialize_database, get_search_history, clear_search_history
from agricultural_database import initialize_agr_database
from auth import create_remember_token, authenticate_remember_token, revoke_token

load_dotenv()

st.set_page_config(
    page_title="Weather Forecasting System with Agricultural Analysis",
    page_icon="🌦️",
    layout="wide"
)

initialize_database()
initialize_agr_database()

cookies = stx.CookieManager(key="weather_forecasting_system_cookie_manager")

if "user" not in st.session_state:
    remembered_token = cookies.get("remember_token")
    remembered_user = authenticate_remember_token(remembered_token)
    if remembered_user:
        st.session_state["user"] = remembered_user

if (
    st.session_state.get("user")
    and st.session_state.pop("remember_requested", False)
):
    token = create_remember_token(st.session_state["user"]["user_id"])
    cookies.set(
        cookie="remember_token",
        value=token,
        key="set_remember_token",
        expires_at=datetime.now() + timedelta(days=30),
        path="/",
        same_site="lax",
    )

user = st.session_state.get("user")

if user and st.session_state.get("show_auth"):
    st.session_state["show_auth"] = False

with st.sidebar:
    st.header("Account & Session")
    if user:
        st.success(f"Logged in: {user['username']}")
        if st.button("Log out", use_container_width=True):
            token = cookies.get("remember_token")
            revoke_token(token)
            cookies.delete("remember_token", key="delete_remember_token")
            st.session_state.pop("user", None)
            st.session_state.pop("weather_result", None)
            st.session_state["show_auth"] = False
            st.rerun()
    else:
        st.write("Browsing as **Public Visitor**")
        if st.session_state.get("show_auth"):
            if st.button("← Back to Weather Dashboard", use_container_width=True):
                st.session_state["show_auth"] = False
                st.rerun()
        else:
            if st.button("Log in / Create Account", type="primary", use_container_width=True):
                st.session_state["show_auth"] = True
                st.rerun()
        st.caption(
            "Sign in with a unique username to unlock Advanced Weather charts, "
            "Agricultural Analysis, and Personal Search History."
        )

if not user and st.session_state.get("show_auth"):
    show_auth_page()
else:
    st.title("🌦️ Weather Forecasting System with Agricultural Analysis")
    if user:
        st.write(
            f"Welcome back, **{user['username']}**! You have full access to Basic Weather, "
            "Advanced Weather trends, Agricultural Analysis, and your Personal Search History."
        )
    else:
        st.write(
            "Search any city for **Basic Weather** forecasts. Log in or create an account to unlock "
            "**Advanced Weather**, **Agricultural Analysis**, and **Personal Search History**."
        )

    city = st.text_input("Enter city name", placeholder="e.g., New Delhi")
    view_guest_page(city)

    st.divider()
    st.subheader("Personal Search History")

    if user:
        history = get_search_history(user["user_id"])
        if history:
            history_df = pd.DataFrame(history).rename(columns={
                "city": "City",
                "country": "Country",
                "temperature": "Temperature (°C)",
                "humidity": "Humidity (%)",
                "weather_code": "Weather Code",
                "searched_at": "Search Date & Time (UTC)",
            })
            st.dataframe(history_df, use_container_width=True, hide_index=True)

            if st.button("Clear Search History"):
                clear_search_history(user["user_id"])
                st.success("Search history cleared.")
                st.rerun()
        else:
            st.info("No saved searches yet. Search for a valid city above to record it in your personal history.")
    else:
        st.info("Log in with your username to save and revisit your personal search history.")