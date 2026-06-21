from cryptography.fernet import Fernet
from datetime import datetime
from dotenv import load_dotenv
from py_send_m365 import M365Mail
from random import shuffle
from string import ascii_uppercase as au, ascii_lowercase as al, digits

import bcrypt
import logging
import os
import pyclamd
import pyotp
import qrcode
import secrets
import smtplib
import streamlit as st


load_dotenv()
app_password = os.getenv('APP_PASSWORD')
mail_from = os.getenv('MAIL_FROM')
db_name = os.getenv('DB_NAME')
db_username = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
email_address = os.getenv('EMAIL')
encryption_key = os.getenv('ENCRYPTION_KEY')
file_key = Fernet(encryption_key)

DB_CONFIG = {'host': db_host, 'password': db_password, 'user': db_username, 'database': db_name, }

mailer = M365Mail("iboadi@pdaghana.com", password=app_password, host="smtp.office365.com", port=587)
cd = pyclamd.ClamdUnixSocket()
user_actions = ["UPLOAD FILE", "DOWNLOAD FILE", "Upload & Download Files", "Administrator"]
path = "/home/pdaghana/Documents/windows_server/VSCode_Projects/streamlit-staging"

def log_file():
    now = datetime.now()
    logging.basicConfig(filename=f'logs/{now.year}-{now.month}-{now.day}.log', encoding='utf-8')


def log_info(statement):
    log_file()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    cur_time = datetime.now()
    logging.info(f'{cur_time}: {statement}')


def log_warning(statement):
    log_file()
    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
    cur_time = datetime.now()
    logging.warning(f'{cur_time}: {statement}')


def hash_text(username=None):
    if username:
        hash_output = bcrypt.hashpw(username.encode('utf-8'), bcrypt.gensalt(12))
        return hash_output

    pw = [secrets.choice(au) for _ in range(5)] + \
         [secrets.choice(al) for _ in range(5)] + \
         [secrets.choice(digits) for _ in range(4)] + \
         [secrets.choice(".;,-") for _ in range(2)]

    shuffle(pw)
    pw = ''.join(pw)
    hashed_pw = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
    return hashed_pw, pw
def setup_mfa(username, full_name):
    secret_key = pyotp.random_base32()
    totop_auth = pyotp.totp.TOTP(secret_key).provisioning_uri(
        name=full_name, issuer_name="PDA File Sharing system")
    qrcode.make(totop_auth).save(f"qrcodes/{username}_qrcode.png")
    encrypted_key = file_key.encrypt(secret_key.encode())
    return encrypted_key


def send_email(full_name, receiver_email, username=None, pw=None, token=None):
    with open('/home/pdaghana/Documents/windows_server/VSCode_Projects/streamlit-staging/assets/credentials_email.txt',
              'r') as file:
        credentials_message = file.read()

    with open('/home/pdaghana/Documents/windows_server/VSCode_Projects/streamlit-staging/assets/message.txt',
              'r') as file:
        token_message = file.read()

    if not token:
        try:
            mailer.send_mail(receiver_email, "User credentials for PDA system",
                             credentials_message.format(full_name.split()[0], username, pw, receiver_email,
                                                        full_name))
            log_info(f'Email with credentials for {full_name} sent to their email address {receiver_email}.')
            return True
        except smtplib.SMTPException as e:
            st.error("")
            return False

    else:
        mailer.send_mail(receiver_email, 'Token for PDA system',
                         token_message.format(full_name.split()[0], token, full_name))
        log_info(f"Email with token for user {username} sent to {receiver_email}.")
        return True


# def add_bg_from_local(image_file):
#     with open(image_file, "rb") as file:
#         encoded_image = base64.b64encode(file.read()).decode()
#     st.markdown(
#         f"""
#          <style>
#          .stApp {{
#              background-image: url("data:image/png;base64,{encoded_image}");
#              background-size: cover;
#              background-position: center;
#          }}
#          </style>
#          """,
#         unsafe_allow_html=True
#     )
