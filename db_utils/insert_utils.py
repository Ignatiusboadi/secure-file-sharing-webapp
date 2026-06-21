from mysql.connector.pooling import MySQLConnectionPool
from mysql.connector import IntegrityError, DatabaseError
from utils.utils import DB_CONFIG

import streamlit as st

if "pool" not in st.session_state:
    st.session_state["pool"] = MySQLConnectionPool(pool_name="st_app_pool", pool_size=30, **DB_CONFIG)

pool = st.session_state["pool"]


def insert_user(username, full_name, email, hashed_pw, status_id, org_id, secret, user_type):
    with pool.get_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    """INSERT INTO users (username, full_name, email, passwords, status_id, organisation_id, secret, user_type)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (username, full_name, email, hashed_pw, status_id, org_id, secret, user_type))
                conn.commit()
                return True
            except (IntegrityError, DatabaseError):
                conn.rollback()
                return False


def insert_project(project_name, folder_name, org_id):
    active_id = st.session_state["statuses"]["active"]
    with pool.get_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    "INSERT INTO projects(organisation_id, project_name, folder_name, project_status_id) VALUES (%s, %s, %s, %s)",
                    (org_id, project_name, folder_name, active_id))
                conn.commit()
                return True
            except (IntegrityError, DatabaseError):
                conn.rollback()
                return False


def insert_proj_permission(project_id, user_id, permission_id):
    with pool.get_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    """INSERT INTO proj_permissions (project_id, user_id, permission_id)
                    VALUES (%s, %s, %s)""", (project_id, user_id, permission_id))
                conn.commit()
                return True
            except (IntegrityError, DatabaseError):
                conn.rollback()
                return False


def insert_files(file_name, proj_id, user_activity_id):
    with pool.get_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute("INSERT INTO files (file_name, project_id, user_activity_id) VALUES (%s, %s, %s)",
                               (file_name, proj_id, user_activity_id))
                conn.commit()
            except (IntegrityError, DatabaseError):
                conn.rollback()


def insert_user_activity(user_id, activity_id, activity_time, outcome_id, details):
    with pool.get_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute("""INSERT INTO user_activity_logs(user_id, activity_id, activity_time, outcome_id, details) 
                VALUES (%s, %s, %s, %s, %s)""", (user_id, activity_id, activity_time, outcome_id, details))
                latest_act_id = cursor.lastrowid
                conn.commit()
                return latest_act_id
            except (IntegrityError, DatabaseError):
                conn.rollback()


def insert_organisation(organisation):
    with pool.get_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute("INSERT INTO organisations (organisation_name) VALUES (%s)", (organisation,))
                conn.commit()
                return True
            except (IntegrityError, DatabaseError):
                conn.rollback()
                return False
