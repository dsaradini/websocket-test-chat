import getpass
from pbkdf2 import crypt

from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy

import logging
logger = logging.getLogger('utility')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


if __name__ == "__main__":
    cluster = Cluster(
        ['127.0.0.1'],
        load_balancing_policy=DCAwareRoundRobinPolicy(),
        port=9042)
    session = cluster.connect('core')

    username = input("Username:")
    statement = session.prepare("""
        SELECT user_name FROM core.users WHERE user_name=?;
    """)
    rows = session.execute(statement.bind([username]))
    if len(rows):
        logger.error("User already exists")
    else:
        full_name = input("Full name:")
        email = input("email:")
        raw_password = getpass.getpass("Password:")
        raw_password_2 = getpass.getpass("Password again:")
        assert raw_password == raw_password_2
        password = crypt(raw_password)
        print("pwd: {}".format(password))
        statement = session.prepare("""
            INSERT INTO core.users ( user_name, pwd_hash, full_name, email )
            VALUES ( ?, ?, ?, ? );
        """)
        session.execute(statement.bind([username, password, full_name, email]))
        logger.info('User created.')
    session.cluster.shutdown()
    session.shutdown()
    logger.info('Connection closed.')
