import logging, datetime
logging.basicConfig(filename="access.log", level=logging.INFO)

def log_access(user, endpoint):
    logging.info(f"{datetime.datetime.utcnow()} - User {user['sub']} accessed {endpoint}")
