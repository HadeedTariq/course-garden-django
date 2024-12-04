from django.shortcuts import redirect
from authentication import utils
from authentication.models import User
from django import http


class TeacherMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code executed for each request before the view is called.
        if request.path.startswith("/teacher/"):
            access_token = request.COOKIES.get("access_token")
            if not access_token:
                return redirect("/auth/login")
            else:
                user = utils.validate_access_token(access_token)
                try:
                    is_teacher = User.objects.get(
                        username=user["username"],
                        role="teacher",
                    )
                    print(is_teacher)
                except User.DoesNotExist:
                    return http.HttpResponse("Unauthorized")

        response = self.get_response(request)

        # Code executed for each request after the view is called.
        return response
