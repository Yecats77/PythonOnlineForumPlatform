from functools import wraps
from flask import session, url_for, redirect


# Login restriction decorator for certain web pages that can only be viewed by logged in users
def login_limit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check whether email is assigned in the session. If yes, you are logged in.
        if session.get('email'):
            # If logged in, access the function normally
            return func(*args, **kwargs)
        else:
            # If not logged in, redirect it to the login page. 
            # Here you can also write a permission error prompt page to jump.
            return redirect(url_for('login'))

    return wrapper
