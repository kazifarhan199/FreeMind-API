from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import TokenAuthentication
from accounts.models import Device
from rest_framework import exceptions, HTTP_HEADER_ENCODING

class DeviceAuthentication(TokenAuthentication):

    def get_deviceToken(self, request):
        auth = request.META.get('HTTP_DEVICE', '')
        # if isinstance(auth, str):
        #     # Work around django test client oddness
        #     auth = auth.encode(HTTP_HEADER_ENCODING)
        return auth

    def authenticate(self, request):
        data = super().authenticate(request)  # user, token
        if data:
            devicetoken = self.get_deviceToken(request)
            if Device.objects.filter(user=data[0], devicetoken=devicetoken).exists():
                return data
            else:
                msg = _('Device token not valid')
                raise exceptions.AuthenticationFailed(msg)

        return data
