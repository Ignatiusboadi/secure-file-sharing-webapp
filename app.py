from main import main_dashboard
from views.login import login_page
from utils.utils import log_info

import streamlit as st

from db_utils.fetch_utils import load_values


if "permissions" not in st.session_state:
    load_values()

st.set_page_config(page_title="DATA UPLOAD")
if "credentials_verified" not in st.session_state:
    st.session_state['credentials_verified'] = False
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'token_sent' not in st.session_state:
    st.session_state['token_sent'] = False
if 'login_tries' not in st.session_state:
    st.session_state['login_tries'] = 0
if 'user_locked_out' not in st.session_state:
    st.session_state['user_locked_out'] = False
if 'new_user' not in st.session_state:
    st.session_state['new_user'] = False
if 'secret' not in st.session_state:
    st.session_state['secret'] = None
if "pool_created" not in st.session_state:
    st.session_state["pool_created"] = False

st.markdown("<h1 style='text-align: center; color: white;'>PDA SECURE FILE SHARING PORTAL</h1>", unsafe_allow_html=True)

def main():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if st.session_state['authenticated']:
        log_info(f'Main dashboard displayed for user {st.session_state["username"]}')
        main_dashboard()
    else:
        log_info('Login page displayed.')
        login_page()

if __name__ == '__main__':
    main()