import streamlit as st

from auth import register_user, authenticate_user


def show_auth_page():
    st.title("Account Access🔐")
    login_tab, register_tab = st.tabs(["Log in", "Create account"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Enter Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            remember = st.checkbox("Remember Me on This Device")
            submitted = st.form_submit_button("Log in", type="primary")

        if submitted:
            user = authenticate_user(username, password)
            if user:
                st.session_state["user"] = user
                st.session_state["remember_requested"] = remember
                st.success("Logged in successfully.")
                st.rerun()
            else:
                st.error("Incorrect username or password.")

    with register_tab:
        with st.form("register_form"):
            new_username = st.text_input("Username", key="register_username")
            new_password = st.text_input("Password", type="password", key="register_password")
            confirm_password = st.text_input(
                "Confirm password", type="password", key="register_confirm_password"
            )
            submitted = st.form_submit_button("Create account", type="primary")

        if submitted:
            success, message = register_user(
                new_username, new_password, confirm_password
            )
            if success:
                st.success(message)
            else:
                st.error(message)
