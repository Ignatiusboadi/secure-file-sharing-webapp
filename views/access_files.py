import os
import streamlit as st

from db_utils.fetch_utils import fetch_access_folders
from utils.user_utils import log_user_activity


def access_files(user_id):
    col1, col2 = st.columns([4, 1])
    read_id = st.session_state["permissions"]["Read"]
    read_write_id = st.session_state["permissions"]["Read & Write"]
    if col1.button("🔄Refresh list", key="access-files-list"):
        proj_folders = fetch_access_folders(user_id, read_id, read_write_id)
    else:
        proj_folders = fetch_access_folders(user_id, read_id, read_write_id)
    folders = sorted(proj_folders.keys())
    col1, col2 = st.columns([3, 1])
    col1.write("**Projects**")
    col2.write("**Download**")
    user_type = st.session_state["user_type"]
    subdirs = ["external"] if user_type == st.session_state["user_types"]["partner"] else ["internal", "external"]
    for folder_name in folders:
        for subdir in subdirs:
            if os.path.exists(f"C/zipfiles/{folder_name}_{subdir}.zip"):
                col1, col2 = st.columns([3, 1])
                col1.write(f"{proj_folders[folder_name].upper()} - {folder_name.upper().replace('_', ' ')} - {subdir.title()}")

                with open(f"C/zipfiles/{folder_name}_{subdir}.zip", "rb") as f:
                    downloaded = col2.download_button(
                        label="⬇️Download",
                        data=f,
                        file_name=f"{proj_folders[folder_name]}_{folder_name}_{subdir}.zip",
                        key=f"download_{folder_name}_{subdir}")
                    if downloaded:
                        log_user_activity(user_id, f"{subdir} file download", "success",
                                          f"{user_id} downloaded data for {subdir} files for {proj_folders[folder_name]}")
