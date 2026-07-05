from . import db_helper

def authenticate_credentials(username, password):
    """Verifies credentials and returns user details if valid."""
    user = db_helper.authenticate_user(username, password)
    if user:
        return user
    return None
