from utils.auth_utils import verify_auth_token, check_credential, lock_user, unlock_user
from db_utils.fetch_utils import *
from time import sleep
from utils.user_utils import log_user_activity, modify_user_status
from utils.utils import log_info, log_warning

import streamlit as st

def login_page():
    if not st.session_state['credentials_verified']:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("🔓Login")

            if login_button:
                if not username.strip() or not password.strip():
                    st.warning("Invalid credentials")
                    log_warning("username and/or password input box empty")
                    st.stop()
                user_status = fetch_user_status(username)
                st.session_state["user_status"] = user_status
                if not user_status:
                    st.warning("Invalid username or password. Please try again.")
                    log_user_activity(0, "account login", "failed",
                                      "Credentials used for login attempt are unknown")
                    log_warning(f"login attempt unsuccessful with username: {username}")
                    st.stop()

                st.session_state["username"] = username
                st.session_state["userid"], st.session_state["full_name"], st.session_state["secret"], st.session_state["user_type"] = fetch_user_details(username)
                userid = st.session_state["userid"]
                if user_status in ["suspended", "archived"]:
                    st.warning("Invalid username or password. Please try again.")
                    log_user_activity(userid, "account login", "failed",
                                      f"Invalid password provided for user with ID {userid}")
                    log_warning(f"login attempt unsuccessful for username: {username}")
                    st.stop()
                if user_status == "locked":
                    unlock_user(userid)
                    user_status = fetch_user_status(username)

                    if user_status == "locked":
                        log_warning(f"locked user with username: {username} attempted login.")
                        st.warning(
                            "You have been locked out after too many attempts. Please try again later."
                        )
                        st.stop()

                if check_credential(username, password):
                    st.session_state["credentials_verified"] = True
                    log_user_activity(userid, "account login", "success",
                                      f"{userid} successfully logged in.")
                    log_info("User successfully logged in.")
                    st.rerun()
                else:
                    log_user_activity(userid, "account login", "failed",
                                      f"{userid} failed to login with provided credentials.")
                    log_warning(f"User, {username}, credentials could not be verified.")
                    st.warning("Invalid credentials")
                    lock_user(userid, "account login")
                    log_info(f"User {username} locked out of system")
                    st.stop()

    else:
        user_status = st.session_state["user_status"]
        userid = st.session_state["userid"]
        if user_status == "pending activation":
            st.markdown("Use **Google Authenticator** or **Microsoft Authenticator** to scan this QR code, then enter the token generated in the authenticator app in the box below for verification.")
            st.image(f"qrcodes/{st.session_state['username']}_qrcode.png", width=300)
            st.write("")

        with st.form("verify-form"):
            auth_token = st.text_input("Enter the token from your authenticator.")
            submitted = st.form_submit_button("Verify")
            if submitted:
                result = verify_auth_token(auth_token, st.session_state["secret"], st.session_state["userid"],
                                           user_status)
                if result:
                    st.session_state["authenticated"] = True
                    st.session_state["credentials_verified"] = False
                    st.session_state["secret"] = ""
                    log_user_activity(userid, "mfa authentication", "success",
                                      f"MFA for {userid} successfull.")
                    log_info(f"User with username {st.session_state['username']} authenticated successfully.")
                    modify_user_status(userid, "active")
                    st.rerun()
                else:
                    log_user_activity(userid, "mfa authentication", "failed",
                                      f"MFA for {userid} failed")
                    log_warning(f"User entered a wrong token.")
                    st.error("Wrong token")
                    if lock_user(userid, "mfa authentication"):
                        st.session_state["credentials_verified"] = False
                        st.warning("You have been locked out after too many attempts. Please try again later.")
                        log_warning(f"User with username {st.session_state['username']} locked out successfully.")
                        sleep(5)
                        st.rerun()
