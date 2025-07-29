from functools import lru_cache, wraps

from flask import request
from flask_basicauth import BasicAuth


class MultiuserBasicAuth(BasicAuth):
    def __init__(
        self, app, admins=None, users=None, login_callback=None, enforce=False
    ):
        super(MultiuserBasicAuth, self).__init__(app)
        self.admins = admins
        self.users = users
        self.login_callback = login_callback
        self.enforce = enforce

    @lru_cache
    def check_credentials(self, username, password, admin):
        if admin:
            success = username in self.admins and self.admins[username] == password
            self.login_callback(username, success)
            return success

        if username in self.users and self.users[username] == password:
            self.login_callback(username, True)
            return True
        else:
            return self.check_credentials(username, password, True)

    def authenticate(self, admin):
        auth = request.authorization
        return (
            auth
            and auth.type == "basic"
            and self.check_credentials(auth.username, auth.password, admin)
        )

    def user_required(self, view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if (not self.enforce) or self.authenticate(False):
                return view_func(*args, **kwargs)
            else:
                return self.challenge()

        return wrapper

    def admin_required(self, view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if (not self.enforce) or self.authenticate(True):
                return view_func(*args, **kwargs)
            else:
                return self.challenge()

        return wrapper

    def current_user(self) -> str:
        if not self.enforce:
            return "-"

        try:
            auth = request.authorization
            if auth and auth.type == "basic":
                return f"{auth.username}"
            else:
                return "-"
        except:
            return "[suvi]"
