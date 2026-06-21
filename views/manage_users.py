from db_utils.insert_utils import insert_proj_permission
from db_utils.fetch_utils import *
from db_utils.modify_utils import delete_user, update_permission
from utils.user_utils import modify_user_status, log_user_activity
from utils.utils import log_warning

import streamlit as st


def manage_users(user_id):
    # if st.button("Log out", key="manage-users-logout"):
    #     st.session_state['authenticated'] = False
    #     st.rerun()
    exist_active_users = sorted(fetch_active_users())
    active_username = st.selectbox("Username", options=exist_active_users, index=0, key="sel-active-users")
    permissions = st.session_state["permissions"]
    orgs = {item[1]: item[0] for item in fetch_orgs()}
    orgs_dropdown = sorted(orgs.keys())
    organisation = st.selectbox("Organisation", options=orgs_dropdown, index=0, key="proj_org")
    projects = {item[1]: item[0] for item in fetch_projects(orgs[organisation])}
    if projects:
        proj_dropdown = sorted(projects.keys())
        project = st.selectbox("Project", options=proj_dropdown, index=0, key="project")
        proj_id = projects[project]
        perm_dropdown = sorted(permissions.keys())
        permission = st.selectbox("Permission", options=perm_dropdown, index=0, key="permission")

        # with st.form(key="manage-users"):
        #     username = st.text_input("Username")
        if st.button("✏️Update user"):
            try:
                user_details = fetch_user_details(active_username)
                update_user_id, _, _, _ = user_details
                update_output = update_permission(update_user_id, proj_id, permissions[permission])
                if update_output:
                    log_user_activity(user_id, "account update","success",
                                      f"account for {active_username} with id: {update_user_id} has been updated")
                    st.success(f"Access/permissions for {active_username} updated successfully.")
                else:
                    update_insert_ouptput = insert_proj_permission(proj_id, update_user_id, permissions[permission])
                    if update_insert_ouptput:
                        log_user_activity(user_id, "account update","success",
                                          f"account for {active_username} with id: {update_user_id} has been updated")
                        st.success(f"Access/permissions for {active_username} updated successfully.")
                    else:
                        st.error("User already has the selected permission for the selected project")
            except Exception as e:
                log_user_activity(user_id, "account update", "failed",
                                     f"account update for {active_username} with id: {update_user_id} failed")
                log_warning(f"Account creation failed with error {e} -- {e.__class__.__name__}")
                st.error(f"Account update failed.")
    else:
        st.warning("Organisation has no existing project. Add one before proceeding.")

    st.divider()

    # with st.form(key="reactivate-user"):
    exist_archived_users = sorted(fetch_archived_users())
    re_act_username = st.selectbox("Username", options=exist_archived_users, index=0, key="sel-archived-users")
    button_state = False if re_act_username else True
    if st.button("▶️Re-activate account", key="reactivate-user-submit", disabled=button_state):
        re_act_user_id, _, _, _ = fetch_user_details(re_act_username)
        try:
            modify_user_status(re_act_user_id, "active")
            log_user_activity(user_id, "account re-activation", "success",
                              f"account re-activation of {re_act_username} with id: {re_act_user_id} successful.")
            st.success(f"User {re_act_username} has been re-activated")
        except:
            log_user_activity(user_id, "account re-activation", "failed",
                              f"account re-activation of {re_act_username} with id: {re_act_user_id} failed.")
            log_warning(f"Account re-activation failed with error {e} -- {e.__class__.__name__}")
            st.error(f"Account re-activation not successful.")

    st.divider()

    # with st.form(key="deactivate-user"):
    exist_active_users2 = sorted(fetch_active_users())
    de_act_username = st.selectbox("Username", options=exist_active_users2, index=0, key="sel-active-users2")
    if st.button("🚫Deactivate account", key="deactivate-user-submit"):
        try:
            deactivate_user_id, _, _, _ = fetch_user_details(de_act_username)
            modify_user_status(deactivate_user_id, "archived")
            log_user_activity(deactivate_user_id, "account deactivation", "success",
                              f"account deactivation of {de_act_username} with id: {deactivate_user_id} successful.")
            st.success(f"User {de_act_username} has been deactivated")
        except Exception as e:
            log_user_activity(user_id, "account deactivation", "failed",
                              f"account deactivation of {de_act_username} with id: {deactivate_user_id} failed.")
            log_warning(f"Account deactivation failed with error {e} -- {e.__class__.__name__}")
            st.error(f"Account deactivation not successful.")

    st.divider()

    # with st.form(key="delete-user"):
    exist_all_users = sorted(fetch_all_users())
    del_username = st.selectbox("Username", options=exist_all_users, index=0, key="sel-all-users")
    if st.button("🗑️ Delete account", key="delete-user-submit"):
        del_user_id, _, _, _ = fetch_user_details(del_username)
        try:
            delete_user(del_user_id)
            log_user_activity(user_id, "account deletion", "success",
                              f"account deletion for {del_username} successful")
            st.success(f"User {del_username} has been deleted")
        except Exception as e:
            log_user_activity(user_id, "account deletion", "success",
                              f"account deletion for {del_username} failed")
            log_warning(f"Account deletion failed with error {e} -- {e.__class__.__name__}")
            st.error(f"Account deletion not successful.")
