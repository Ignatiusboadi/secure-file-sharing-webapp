import os
import streamlit as st

from db_utils.fetch_utils import fetch_user_folders
from utils.file_utils import save_uploaded_files
from utils.utils import log_warning, log_info


def upload_files(userid):
    col1, col2 = st.columns([3, 1])
    # if col2.button("Log out", key="upload-files-users-logout"):
    #     st.session_state['authenticated'] = False
    #     st.rerun()
    write_id = st.session_state["permissions"]["Write"]
    read_write_id = st.session_state["permissions"]["Read & Write"]
    if col1.button("🔄Refresh list", key="upload-refresh-list"):
        user_folders = fetch_user_folders(userid, write_id, read_write_id)
    else:
        user_folders = fetch_user_folders(userid, write_id, read_write_id)
    if user_folders:
        project = st.selectbox("Select a project", list(user_folders.keys()))
        if st.session_state["user_type"] == st.session_state["user_types"]["partner"]:
            subdir = "external"
        else:
            subdir = st.radio("Select a subdirectory", ["Internal", "External"])
        if project:
            sel_upload_folder = os.path.join("C", user_folders[project], subdir.lower())
            allowed_extensions = ["zip", "csv", "xlsx", "pdf"]
            uploaded_files = st.file_uploader("Upload files", type=allowed_extensions, accept_multiple_files=True)

        if project and uploaded_files:
            invalid_files = [file.name for file in uploaded_files if
                             file.name.split('.')[-1].lower() not in allowed_extensions]

            if invalid_files:
                st.error(f"Invalid file types: {', '.join(invalid_files)}. Please upload only ZIP, CSV, XLSX or PDF files.")
                log_warning(f"User tried to upload {', '.join(invalid_files)}.")
                st.stop()
            else:
                st.write(f"You have uploaded {len(uploaded_files)} file(s). Click 'Upload Files' to proceed.")
                log_info(f"User {st.session_state['username']} has uploaded {len(uploaded_files)} file(s).")

            if st.button("⬆️Upload Files"):
                try:
                    user_logged_in = st.session_state.get("username", "")
                    uploaded = save_uploaded_files(uploaded_files, sel_upload_folder, subdir.lower(), project)
                    if uploaded:
                        log_info(f"{user_logged_in} uploaded files into {sel_upload_folder}.")
                    else:
                        log_warning(f"{user_logged_in} failed to upload at least one file into {sel_upload_folder} .")
                except Exception as e:
                    log_warning(f"{e}({e.__class__})")
                    uploaded = False

                if uploaded:
                    log_info('Upload successfully done.')
                    st.success("Upload successful!")
                else:
                    log_warning(f'Upload failed for user {st.session_state["username"]}.')
                    st.error(
                        "At least one of your files failed to be uploaded. Please verify they are free from viruses/malware and try again.")
                    st.stop()
