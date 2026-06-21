from db_utils.fetch_utils import fetch_orgs, fetch_orgid
from db_utils.insert_utils import insert_project, insert_organisation
from utils.user_utils import log_user_activity
from utils.utils import log_warning, path

import os
import streamlit as st


def add_org_project(userid):
    # if st.button("Log out", key="add_org_proj-user-logout"):
    #     st.session_state['authenticated'] = False
    #     st.rerun()
    with st.form(key="add_organisation"):
        org_name = st.text_input("Organisation Name").strip()
        if st.form_submit_button("🏢Add organisation"):
            try:
                outcome = insert_organisation(org_name)
                if not outcome:
                    st.warning(f"Organisation **{org_name}** already exists")
                else:
                    st.success(f"Organisation {org_name} added successfully")
                    log_user_activity(userid, "organisation creation", "success",
                                      f"{org_name} added to organisations in database.")
            except Exception as e:
                log_user_activity(userid, "organisation creation", "failed",
                                  f"Attempt to add {org_name} failed.")
                log_warning(f"Error during organisation creation: {e} -- {e.__class__.__name__}")
                st.error("An error occurred while adding organisation.")

    with st.form(key="add_project"):
        project_name = st.text_input("Project Name").strip()
        folder_name = st.text_input("Folder Name").strip()
        orgs = {item[1]: item[0] for item in fetch_orgs()}

        dropdown_options = sorted(orgs.keys())
        if dropdown_options:
            organisation = st.selectbox("Organisation", options=dropdown_options, index=0)
            if st.form_submit_button("📁Add Project"):
                org_id = fetch_orgid(organisation)
                if len(project_name) < 3 or len(folder_name) < 3:
                    st.error("Project/folder name too short.")
                else:
                    try:
                        ins_outcome = insert_project(project_name, folder_name, org_id)
                        if not ins_outcome:
                            st.warning(f"The folder {folder_name} already exists, please choose a different name.")
                            log_user_activity(userid, "project creation", "failed",
                                              f"{project_name} or folder {folder_name} already exists.")
                        else:
                            log_user_activity(userid, "project creation", "success",
                                              f"{project_name} added successfully")
                            os.makedirs(os.path.join(path, f"C/{folder_name}/external"), exist_ok=True)
                            os.makedirs(os.path.join(path, f"C/{folder_name}/internal"), exist_ok=True)
                            st.success(f"Project {project_name} added successfully")
                    except Exception as e:
                        log_user_activity(userid, "project creation", "failed",
                                          f"{project_name} or folder {folder_name} not added.")
                        log_warning(f"Error during project creation: {e} -- {e.__class__.__name__}")
                        st.error("An error occurred while adding project.")
        else:
            st.warning("No organisations available. Please add one first.")
