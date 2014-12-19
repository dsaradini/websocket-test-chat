import getpass
import json
import os
from pbkdf2 import crypt

import logging
logger = logging.getLogger('utility')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


if __name__ == "__main__":
    if os.path.exists("users.json"):
        with open("user.json", mode="r") as f:
            users = json.loads(f.read())
    else:
        users = dict()

    username = input("Username:")
    if username in users:
        logger.error("User already exists")
    else:
        full_name = input("Full name:")
        email = input("email:")
        raw_password = getpass.getpass("Password:")
        raw_password_2 = getpass.getpass("Password again:")
        assert raw_password == raw_password_2
        password = crypt(raw_password)
        print("pwd: {}".format(password))
        users[username] = {
            'user_name': username,
            'password': password,
            'full_name': full_name,
            'email': email
        }
        with open("users.json", mode="w") as f:
            f.write(json.dumps(users))
        logger.info('User created.')
