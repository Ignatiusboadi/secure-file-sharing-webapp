from db_utils.insert_utils import insert_user, insert_proj_permission
from db_utils.fetch_utils import *
from utils.user_utils import log_user_activity
from utils.utils import hash_text, setup_mfa, send_email, log_warning, log_info

import streamlit as st

def add_users(user_id):
    # if st.button("Log out", key="🗑add-users-logout"):
    #     st.session_state['authenticated'] = False
    #     st.rerun()
    statuses = st.session_state["statuses"]
    permissions = st.session_state["permissions"]
    orgs = {item[1]: item[0] for item in fetch_orgs()}
    orgs_dropdown = sorted(orgs.keys())
    organisation = st.selectbox("Organisation", options=orgs_dropdown, index=0, key="new_user_org")
    projects = {item[1]: item[0] for item in fetch_projects(orgs[organisation])}
    if projects:
        proj_dropdown = sorted(projects.keys())
        project = st.selectbox("Project", options=proj_dropdown, index=0, key="new_user_project")
        proj_id = projects[project]
        perm_dropdown = sorted(permissions.keys())
        permission = st.selectbox("Permission", options=perm_dropdown, index=0, key="new_user_permission")
        with st.form(key="add-users"):
            full_name = st.text_input("Full Name")
            username = st.text_input("Username")
            email = st.text_input("Email")
            user_types = st.session_state["user_types"]
            user_type = st.selectbox("User Type", options=[item.title() for item in sorted(user_types.keys())],
                                     index=0, key="new_user_user_type")
            user_type_id = user_types[user_type.lower()]
            if st.form_submit_button("👤 Add user"):
                if not full_name or not username or not email:
                    st.warning("Please fill out all fields")
                else:
                    try:
                        org_id = orgs[organisation]
                        status_id = statuses["pending activation"]
                        hashed_pw, pw = hash_text()
                        secret = setup_mfa(username, full_name)
                        outcome = insert_user(username, full_name, email, hashed_pw, status_id, org_id, secret, user_type_id)
                        if outcome:
                            new_user_id, _, _, _ = fetch_user_details(username)
                            insert_proj_permission(proj_id, new_user_id, permissions[permission])
                            log_user_activity(user_id, "account creation", "success",
                                              f"account for {full_name} with user id:{new_user_id} created")
                            if send_email(full_name, email, username, pw):
                                log_info("User details successfully shared.")
                                st.success(f"Successfully added {full_name} and shared credentials.")
                            else:
                                log_info("User details not shared due internet issues")
                                st.error("User details not shared due to internet issues. Please delete user and try again.")
                        else:
                            st.error("User account not created, please try again later.")
                    except Exception as e:
                        log_user_activity(user_id, "account creation", "failed",
                                          f"account creation for {full_name} failed")
                        log_warning(f"Account creation failed with error {e} -- {e.__class__.__name__}")
                        st.error(f"Account creation failed for user: {username}.")
    else:
        st.warning("Organisation has no existing project. Add one before proceeding.")
