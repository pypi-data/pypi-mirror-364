import functools
import json

from tornado.options import options

from lesscode.utils.custom_type import User
from lesscode.web.business_exception import BusinessException
from lesscode.web.status_code import StatusCode


def user_verification(username="admin", **kw):
    def wrapper(func):
        @functools.wraps(func)
        def run(self, *args, **kwargs):
            if options.running_env != "local":
                user_str = self.request.headers.get("User")
                if user_str:
                    user = json.loads(user_str)
                    if isinstance(user, dict):
                        user_username = user.get("username")
                        if username != user_username:
                            raise BusinessException(StatusCode.ACCESS_DENIED)
                    else:
                        raise BusinessException(StatusCode.ACCESS_DENIED)
                else:
                    raise BusinessException(StatusCode.ACCESS_DENIED)

            return func(self, *args, **kwargs)

        return run

    return wrapper


def login_verification_func(self, *args, **kwargs):
    if options.running_env != "local":
        user = self.request.headers.get("User")
        if not user:
            raise BusinessException(StatusCode.INVALID_TOKEN)
        else:
            user_info = json.loads(user)
            if not user_info:
                raise BusinessException(StatusCode.INVALID_TOKEN)
    else:
        return User()


def login_verification(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not options.login_verification_func:
            options.login_verification_func = login_verification_func
        options.login_verification_func(self, *args, **kwargs)

        return func(self, *args, **kwargs)

    return wrapper
