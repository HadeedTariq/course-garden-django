from functools import wraps
from django import http
from django.shortcuts import redirect

from authentication import utils


def course_middleware_decorator(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        access_token = request.COOKIES.get("access_token")
        pathname = request.path
        print("path")
        if access_token:
            try:
                user = utils.validate_access_token(access_token)
                request.validation_err = ""
                request.user_data = user
                return view_func(request, *args, **kwargs)
            except Exception as e:
                return http.HttpResponse("Ivalid Token")
        else:
            return redirect(f"/auth/login?next={pathname}")

    return _wrapped_view
