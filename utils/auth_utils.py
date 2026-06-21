from db_utils.modify_utils import update_user_status
from utils.utils import log_info, log_warning, file_key
from utils.user_utils import modify_user_status, log_user_activity
from db_utils.fetch_utils import *

import bcrypt
import pyotp
import streamlit as st

def check_credential(username, password):
    stored_hashed_password = fetch_user_passwd(username).encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password)

def verify_auth_token(auth_token, secret, user_id, new_user):
    secret = file_key.decrypt(secret)
    totp = pyotp.TOTP(secret.decode())
    if totp.verify(auth_token):
        if new_user:
            modify_user_status(user_id, "active")
        return True
    else:
        return False

def lock_user(userid, activity):
    act_id = st.session_state["activities"][activity]
    count = fetch_user_login_attempts(userid, act_id, 2)
    locked_id = st.session_state["statuses"]["locked"]
    if count > 3:
        update_user_status(userid, locked_id)
        log_user_activity(userid, "lock account", "success",
                          f"user {userid} is locked and temporarily prevented from logging in")
        return True
    return False

def unlock_user(userid):
    active_id = st.session_state["statuses"]["active"]
    pending_mfa_id = st.session_state["statuses"]["pending activation"]
    minutes = fetch_user_locked_time(userid)
    if minutes and minutes > 2:
        if fetch_mfa_setup(userid):
            update_user_status(userid, active_id)
            st.session_state["user_status"] = "active"
        else:
            update_user_status(userid, pending_mfa_id)
            st.session_state["user_status"] = "pending activation"
        log_user_activity(userid, "unlock account", "success",
                          f"user {userid} is now unlocked and can attempt to log in")
        return True
    return False
