from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "roles" not in session or role_name not in session["roles"]:
                flash("Unauthorized access", "danger")
                return redirect(url_for("auth.login"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
