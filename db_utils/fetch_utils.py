from mysql.connector.pooling import MySQLConnectionPool
from utils.utils import DB_CONFIG

import streamlit as st


if "pool" not in st.session_state:
    st.session_state["pool"] = MySQLConnectionPool(pool_name="st_app_pool", pool_size=30, **DB_CONFIG)

pool = st.session_state["pool"]

def load_values():
    with pool.get_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:

            cursor.execute("SELECT ID, permission_name FROM permissions")
            perm_results = cursor.fetchall()
            st.session_state["permissions"] = {row["permission_name"]: row["ID"] for row in perm_results} \
                if perm_results else None

            cursor.execute("SELECT ID, outcome FROM outcomes")
            outcome_results = cursor.fetchall()
            st.session_state["outcomes"] = {row["outcome"]: row["ID"] for row in outcome_results} \
                if outcome_results else None

            cursor.execute("SELECT ID, activity_name FROM activities")
            activity_results = cursor.fetchall()
            st.session_state["activities"] = {row["activity_name"]: row["ID"] for row in activity_results} \
                if activity_results else None

            cursor.execute("SELECT ID, status_name FROM user_status")
            status_results = cursor.fetchall()
            st.session_state["statuses"] = {row["status_name"]: row["ID"] for row in status_results} \
                if status_results else None

            cursor.execute("SELECT ID, user_type_name FROM user_types")
            types_results = cursor.fetchall()
            st.session_state["user_types"] = {row["user_type_name"]: row["ID"] for row in types_results}
            st.session_state["rev_user_types"] = {row["ID"]: row["user_type_name"] for row in types_results}

def fetch_user_details(username):
    with pool.get_connection() as conn:
        with conn.cursor(buffered=True) as cursor:
            cursor.execute("SELECT user_id, full_name, secret, user_type_id FROM users WHERE username=%s", (username,))
            results = cursor.fetchone()
            if results:
                userid_secret = results
            else:
                userid_secret = None
            return userid_secret

def fetch_permissions():
    with pool.get_connection() as conn:
        with conn.cursor(buffered=True) as cursor:
            cursor.execute("SELECT ID, permission_name FROM permissions")
            results = cursor.fetchall()
            return results

def fetch_orgid(organisation):
    with pool.get_connection() as conn:
        with conn.cursor(buffered=True) as cursor:
            cursor.execute("SELECT ID FROM organisations WHERE organisation_name=%s", (organisation,))
            results = cursor.fetchone()
            if results:
                org_id = results[0]
            else:
                org_id = None
            return org_id

def fetch_projid(project):
    with pool.get_connection() as conn:
        with conn.cursor(buffered=True) as cursor:
            cursor.execute("SELECT ID FROM projects WHERE project_name=%s", (project,))
            result = cursor.fetchone()
            return result[0]

def fetch_projects(org_id):
    with pool.get_connection() as conn:
        with conn.cursor(buffered=True) as cursor:
            cursor.execute("SELECT ID, project_name FROM projects WHERE organisation_id=%s", (org_id,))
            results = cursor.fetchall()
            return results

def fetch_orgs():
    with pool.get_connection() as conn:
        with conn.cursor(buffered=True) as cursor:
            cursor.execute("SELECT ID, organisation_name FROM organisations")
            results = cursor.fetchall()
            return results


def fetch_user_status(username):
    with pool.get_connection() as conn:
        with conn.cursor(buffered=True) as cursor:
            cursor.execute("""SELECT u_s.status_name FROM users AS u INNER JOIN user_status AS u_s
             ON u.status_id = u_s.ID WHERE u.username=%s""",
                           (username,))
            results = cursor.fetchone()
            if results:
                status = results[0]
            else:
                status = None
            return status

def fetch_project_status(project_id):
    with pool.get_connection() as conn:
        with conn.cursor(buffered=True) as cursor:
            cursor.execute("""SELECT u_s.status_name FROM projects p INNER JOIN user_status u_s 
            ON p.project_status = u_s.ID WHERE p.ID=%s""",
                (project_id,))
            results = cursor.fetchone()
            if results:
                status = results[0]
            else:
                status = None
            return status

def fetch_user_passwd(username):
    with pool.get_connection() as conn:
        with conn.cursor(buffered=True) as cursor:
            cursor.execute("SELECT passwords FROM users WHERE username=%s", (username,))
            results = cursor.fetchone()
            if results:
                password = results[0]
            else:
                password = ""
            return password

def fetch_user_login_attempts(user_id, activity_id, minutes):
    outcome_id = st.session_state["outcomes"]["failed"]
    with pool.get_connection() as conn:
        with conn.cursor(buffered=True) as cursor:
            cursor.execute("""SELECT COUNT(activity_time) FROM user_activity_logs WHERE user_id=%s AND activity_id=%s AND 
                outcome_id=%s AND activity_time >= NOW() - INTERVAL %s MINUTE""",
                (user_id, activity_id, outcome_id, minutes))
            results = cursor.fetchone()
            if results:
                user_activities_count = results[0]
            else:
                user_activities_count = None
            return user_activities_count

def fetch_user_locked_time(user_id):
    act_id = st.session_state["activities"]["lock account"]
    with pool.get_connection() as conn:
        with conn.cursor(buffered=True) as cursor:
            cursor.execute("""SELECT TIMESTAMPDIFF(MINUTE, MAX(activity_time), NOW()) FROM user_activity_logs
             WHERE user_id=%s AND activity_id=%s""", (user_id, act_id))
            results = cursor.fetchone()
            if results:
                minutes_locked = results[0]
            else:
                minutes_locked = None
            return minutes_locked

def fetch_mfa_setup(user_id):
    mfa_id = st.session_state["activities"]["mfa authentication"]
    outcome_id = st.session_state["outcomes"]["success"]
    with pool.get_connection() as conn:
        with conn.cursor(buffered=True) as cursor:
            cursor.execute("""SELECT COUNT(activity_time) FROM user_activity_logs WHERE user_id=%s AND activity_id=%s AND 
                    outcome_id=%s""",
                           (user_id, mfa_id, outcome_id))
            results = cursor.fetchone()
            if results:
                user_activities_count = results[0]
            else:
                user_activities_count = None
            return user_activities_count

def fetch_user_types():
    with pool.get_connection() as conn:
        with conn.cursor(buffered=True) as cursor:
            cursor.execute("SELECT user_type_name FROM user_types;")
            results = cursor.fetchall()
            return [result[0] for result in results]

def fetch_user_folders(user_id, permission_id, read_write_id):
    with pool.get_connection() as conn:
        with conn.cursor(buffered=True) as cursor:
            cursor.execute("""SELECT p.project_name as proj_name, p.folder_name as folder_name FROM 
            projects p INNER JOIN proj_permissions p_p ON p.ID = p_p.project_id
            WHERE p_p.user_id=%s AND p_p.permission_id IN (%s, %s)""", (user_id, permission_id, read_write_id))
            results = cursor.fetchall()
            return {result[0]: result[1] for result in results}

def fetch_proj_files(proj_id):
    with pool.get_connection() as conn:
        with conn.cursor(buffered=True) as cursor:
            cursor.execute("""SELECT DISTINCT(file_name) FROM files WHERE project_id=%s""", (proj_id,))
            results = cursor.fetchall()
            return [result[0] for result in results]

def fetch_access_folders(user_id, read_id, read_write_id):
    with pool.get_connection() as conn:
        with conn.cursor(buffered=True) as cursor:
            cursor.execute("""
            SELECT p.folder_name, p.project_name FROM projects p INNER JOIN proj_permissions as p_p
            ON p.ID = p_p.project_id WHERE p_p.permission_id IN (%s, %s) AND p_p.user_id = %s;""",
                           (read_id, read_write_id, user_id))
            results = cursor.fetchall()

            return {result[0]: result[1] for result in results}

def fetch_user_projects_views():
    with pool.get_connection() as conn:
        with conn.cursor(buffered=True, dictionary=True) as cursor:
            cursor.execute("SELECT * FROM user_projects")
            results = cursor.fetchall()
            return results

def fetch_active_users():
    active_id = st.session_state["statuses"]["active"]
    with pool.get_connection() as conn:
        with conn.cursor(buffered=True) as cursor:
            cursor.execute("""SELECT DISTINCT(username) FROM users WHERE status_id=%s""", (active_id,))
            results = cursor.fetchall()
            return [result[0] for result in results]

def fetch_archived_users():
    with pool.get_connection() as conn:
        with conn.cursor(buffered=True) as cursor:
            cursor.execute("SELECT username FROM users WHERE status_id=%s;",
                           (st.session_state["statuses"]["archived"],))
            results = cursor.fetchall()
            return [result[0] for result in results]

def fetch_all_users():
    with pool.get_connection() as conn:
        with conn.cursor(buffered=True) as cursor:
            cursor.execute("SELECT username FROM users;")
            results = cursor.fetchall()
            return [result[0] for result in results]
