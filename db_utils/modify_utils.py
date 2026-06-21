from mysql.connector.pooling import MySQLConnectionPool
from utils.utils import DB_CONFIG

import streamlit as st

if "pool" not in st.session_state:
    st.session_state["pool"] = MySQLConnectionPool(pool_name="st_app_pool", pool_size=30, **DB_CONFIG)

pool = st.session_state["pool"]

def update_user_status(user_id, status_id):
    with pool.get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET status_id=%s WHERE user_id=%s", (status_id, user_id))
            conn.commit()
            return cursor.rowcount > 0

def update_username_passwd(user_id, username, password):
    with pool.get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET passwords=%s, username=%s WHERE user_id=%s", (password, username, user_id))
            conn.commit()
            return cursor.rowcount > 0

def update_permission(user_id, project_id, permission):
    with pool.get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE proj_permissions SET permission_id=%s WHERE user_id=%s AND project_id=%s",
                           (permission, user_id, project_id))
            conn.commit()
            return cursor.rowcount > 0

def update_project_status(project_id, status):
    with pool.get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE projects SET project_status_id=%s WHERE id=%s", (status, project_id))
            conn.commit()
            return cursor.rowcount > 0

def delete_user(user_id):
    with pool.get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
            conn.commit()
            return cursor.rowcount > 0
