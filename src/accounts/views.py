import random
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework import permissions
from rest_framework import response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from rest_framework.authtoken.views import ObtainAuthToken
from groups.models import GroupsMember, Groups
from django.conf import settings
from .models import OTP, Device
from .utils import check_otp_http_response_if_failed, send_otp_email
from . import serializers


User = get_user_model()


class Register(CreateAPIView):
    """Register"""
    model = User
    permission_classes = [
        permissions.AllowAny # Or anon users can't register
    ]
    serializer_class = serializers.UserSerializer

    def post(self, request):
        if not request.data.get('devicetoken'):
            return Response({'devicetoken': ['This field is required', ]}, status=status.HTTP_400_BAD_REQUEST) 
        if not request.data.get('devicename'):
            return Response({'devicename': ['This field is required', ]}, status=status.HTTP_400_BAD_REQUEST) 
        if not request.data.get('devicetype'):
            return Response({'devicetype': ['This field is required', ]}, status=status.HTTP_400_BAD_REQUEST) 

        respense = super().post(request)
        if (respense.data.get('id')):
            user = User.objects.get(pk=respense.data['id'])
            if Device.objects.filter(devicetoken=request.data['devicetoken']).exists():
                Device.objects.filter(devicetoken=request.data['devicetoken']).delete()
            Device.objects.create(user=user, devicetoken=request.data['devicetoken'], devicename=request.data['devicename'], devicetype=request.data['devicetype'])
            
            return Response(serializers.UserSerializer(user).data)
        else:
            return respense


class Login(ObtainAuthToken):
    """Login and add device to user"""
    def post(self, request, *args, **kwargs):
        '''Login'''
        if not request.data.get('devicetoken'):
            return Response({'devicetoken': ['This field is required', ]}, status=status.HTTP_400_BAD_REQUEST) 
        if not request.data.get('devicename'):
            return Response({'devicename': ['This field is required', ]}, status=status.HTTP_400_BAD_REQUEST) 
        if not request.data.get('devicetype'):
            return Response({'devicetype': ['This field is required', ]}, status=status.HTTP_400_BAD_REQUEST) 

        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if Device.objects.filter(devicetoken=request.data['devicetoken']).exists():
            Device.objects.filter(devicetoken=request.data['devicetoken']).delete()
        Device.objects.create(user=user, devicetoken=request.data['devicetoken'], devicename=request.data['devicename'], devicetype=request.data['devicetype'])

        return Response(serializers.UserSerializer(user).data)


class Logout(APIView):

    def delete(self, request):
        if not request.data.get('devicetoken'):
            return Response({'devicetoken': ['This field is required', ]}, status=status.HTTP_400_BAD_REQUEST) 
        if Token.objects.filter(user=request.user).exists() and Device.objects.filter(user=request.user, devicetoken=request.data['devicetoken']).exists():
            Device.objects.filter(user=request.user, devicetoken=request.data['devicetoken']).delete()
            Token.objects.filter(user=request.user).delete()
            return Response({'detail': ['logged out']}, status=status.HTTP_202_ACCEPTED)
            
        return Response({'detail': ['Some error occured', ]}, status=status.HTTP_400_BAD_REQUEST) 



class Profile(APIView):
    def get(self, request):
        '''Profile'''
        if request.GET.get('user'):
            if User.objects.filter(pk=request.GET.get('user')).exists():
                user = User.objects.get(pk=request.GET.get('user'))
                # g1 = [g.group.id for g in GroupsMember.objects.filter(user=user)]
                # g2 = [g.group.id for g in GroupsMember.objects.filter(user=request.user)]
                # if set(g1)&set(g2):
                    # return Response(serializers.UserProfileSerializer(user).data)
                return Response(serializers.UserProfileSerializer(user).data)

        return Response(serializers.UserSerializer(request.user).data)


class Edit(APIView):
    def put(self, request):
        '''Edit Profile/Change Password'''
        serializer = serializers.UserSerializer(instance=request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordReset(APIView):
    permission_classes = [
        permissions.AllowAny # Or anon users can't register
    ]
    def post(self, request):
        if request.data.get('email') and request.data.get('otp') and request.data.get('password'):
            """Reset password"""
            check = check_otp_http_response_if_failed(request.data['email'], request.data['otp'])
            if check is True:
                user = User.objects.get(email=request.data['email'])
                serializer = serializers.UserSerializer(data=request.data, instance=user)
                if serializer.is_valid():
                    serializer.save()
                    otp = OTP.objects.get(
                        email=request.data['email'], 
                        otp=request.data['otp'],
                    )
                    otp.delete()
                    return Response({"detail": ["Password reset Successful", ]})
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            else:
                return Response({"otp": ["PIN has expired.",]}, status=status.HTTP_400_BAD_REQUEST)

        elif request.data.get('email') and request.data.get('otp'):
            """Check otp"""
            check = check_otp_http_response_if_failed(request.data['email'], request.data['otp'])
            if check is True:
                return Response({"detail": ["Valid PIN", ]})
            else:
                return Response({"otp": ["PIN has expired.",]}, status=status.HTTP_400_BAD_REQUEST)


        elif request.data.get('email'):
            """Send otp"""
            data = {'email': request.data.get('email'), 'otp': str(random.randrange(100000, 999999))}
            serializer = serializers.OTPSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                send_otp_email(data['email'], data['otp'])
                return Response({"detail": ["An email will be sent to your emaill", ]}, status=status.HTTP_201_CREATED)

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"email": ["This field is required", ]}, status=status.HTTP_400_BAD_REQUEST)


class Devices(APIView):
    def get(self, request):
        """Get user device list"""
        return Response(serializers.DeviceSerializer(Device.objects.filter(user=request.user), many=True).data)

    def delete(self, request):
        """Remove device"""
        if not request.data.get('devicetoken'):
            return Response({"devicetoken": ["This field is required", ]}, status=status.HTTP_400_BAD_REQUEST)

        if Device.objects.filter(user=request.user, devicetoken=request.data.get('devicetoken')).exists():
            Device.objects.filter(user=request.user, devicetoken=request.data.get('devicetoken')).delete()
            return Response({"detail": ["device removed", ]}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({"devicetoken": ["Device not found", ]}, status=status.HTTP_404_NOT_FOUND)

