from errno import EACCES

from django import http
from authentication import utils


class StudentMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/student/get-courses"):
            access_token = request.COOKIES.get("access_token")
            if access_token:
                try:
                    user = utils.validate_access_token(access_token)
                    request.user_data = user
                    response = self.get_response(request)
                    return response
                except Exception as e:
                    return http.HttpResponse("Ivalid Token")

            else:
                request.user_data = None
                response = self.get_response(request)
                return response

        else:
            request.validation_err = ""
            response = self.get_response(request)
            return response
