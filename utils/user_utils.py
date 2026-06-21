import pyotp
import qrcode

from datetime import datetime, timezone

from db_utils.insert_utils import insert_user_activity
from db_utils.modify_utils import update_user_status
from utils.utils import log_warning, log_info, file_key, hash_text, user_actions
from mysql.connector.pooling import MySQLConnectionPool
from utils.utils import DB_CONFIG

import bcrypt
import streamlit as st


if "pool" not in st.session_state:
    st.session_state["pool"] = MySQLConnectionPool(pool_name="st_app_pool", pool_size=30, **DB_CONFIG)

pool = st.session_state["pool"]

def log_user_activity(userid, user_action, outcome, details):
    activity_id = st.session_state["activities"][user_action]
    activity_time = datetime.now(timezone.utc)
    outcome_id = st.session_state["outcomes"][outcome]
    return insert_user_activity(userid, activity_id, activity_time, outcome_id, details)

def modify_user_status(userid, status):
    status_id = st.session_state["statuses"][status]
    update_user_status(userid, status_id)
    return True

def add_user(username, full_name, email, password, orgid):
    pass