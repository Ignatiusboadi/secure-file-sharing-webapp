from cryptography.fernet import Fernet

from db_utils.fetch_utils import fetch_projid, fetch_proj_files
from db_utils.insert_utils import insert_files
from utils.user_utils import log_user_activity
from utils.utils import log_info, log_warning, cd
from pathlib import Path

import os
import streamlit as st
import zipfile

def encrypt_file(filename, key):
    f = Fernet(key)
    encrypted_file = filename + ".enc"
    with open(filename, "rb") as infile:
        data = infile.read()
    encrypted = f.encrypt(data)
    with open(encrypted_file, "wb") as outfile:
        outfile.write(encrypted)
    return encrypted_file


def zip_folder(folder_path, zip_filename):
    folder_path = Path(folder_path)
    zip_filename = Path(zip_filename)

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(folder_path.parent)
                zipf.write(file_path, arcname=arcname)


def save_uploaded_files(files, upload_folder, subdir, project):
    os.makedirs(upload_folder, exist_ok=True)
    uploaded = 0
    user_id = st.session_state["userid"]
    proj_id = fetch_projid(project)
    exist_files = fetch_proj_files(proj_id)
    for uploaded_file in files:
        try:
            file_data = uploaded_file.read()
            scan_result = cd.scan_stream(file_data)

            if scan_result is not None:
                log_warning(f"Infected file detected: {uploaded_file.name} -> {scan_result}")
                continue
            file_path = os.path.join(upload_folder, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(file_data)

            log_info(f"Uploaded {uploaded_file.name} into {upload_folder} (clean).")
            if uploaded_file in exist_files:
                user_act = f"{subdir} file update"
            else:
                user_act = f"{subdir} file upload"
            act_id = log_user_activity(user_id, user_act, "success",
                                       f"{user_id} completed an {user_act}")
            proj_id = fetch_projid(project)
            insert_files(uploaded_file.name, proj_id, act_id)
            uploaded += 1

        except Exception as e:
            log_user_activity(user_id, user_act, "failed",
                              f"{user_id} failed to complete an {user_act}")
            log_warning(f"error ({e.__class__})")
    if uploaded:
        try:
            zip_folder(upload_folder, f"C/zipfiles/{"_".join(upload_folder.split('/')[-2:])}.zip")
            log_info(f"Created zip file for {upload_folder}")
        except Exception as e:
            log_warning(f"Could not create zip file for {upload_folder} with error: {e}({e.__class__}).")
    return uploaded == len(files)
