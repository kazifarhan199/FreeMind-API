from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

class DisableCSRFMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)
        response = self.get_response(request)
        return response


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authentication backend which allows users to authenticate using either their
    username or email address

    Source: https://stackoverflow.com/a/35836674/59984
    """

    def authenticate(self, request, username=None, password=None, **kwargs):

        user_model = get_user_model()
        
        if username is None:
            username = kwargs.get(user_model.USERNAME_FIELD)

        users = user_model._default_manager.filter(
            Q(**{user_model.USERNAME_FIELD: username}) | Q(email__iexact=username)
        )

        # Test whether any matched user has the provided password:
        for user in users:
            if user.check_password(password):
                return user

        if not users:
            user_model().set_password(password)


