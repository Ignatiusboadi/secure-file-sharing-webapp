from db_utils.fetch_utils import  *

import streamlit as st
from views.add_org_proj import add_org_project
from views.dashboard import dashboard
from views.manage_users import manage_users
from views.add_user import add_users
from views.upload_files import upload_files
from views.access_files import access_files

# add_bg_from_local("assets/grad.webp")

load_values()

def main_dashboard():
    userid = st.session_state["userid"]
    user_type = st.session_state["user_type"]
    col1, col2 = st.columns([4, 1])
    col1.write(f"""*Logged in as*: **{st.session_state["full_name"]}**""")
    if col2.button("🔐Log out", key="user-logout"):
        st.session_state['authenticated'] = False
        st.rerun()
    if user_type == 1:
        tabs = st.tabs(["Access files", "Upload files", "Projects", "Manage users", "Add user",
                        "Dashboard"])
        with tabs[0]:
            access_files(userid)
        with tabs[1]:
            upload_files(userid)
        with tabs[2]:
            add_org_project(userid)
        with tabs[3]:
            manage_users(userid)
        with tabs[4]:
            add_users(userid)
        with tabs[5]:
            dashboard()
    else:
        tabs = st.tabs(['Upload Files', 'Access Files'])
        with tabs[0]:
            upload_files(userid)
        with tabs[1]:
            access_files(userid)
