import collections
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import OTP, Device

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False, write_only=True)
    email = serializers.EmailField(required=False)

    def validate(self, value):
        data = dict(value)
        if self.instance:
            """Update existing user data"""
            if User.objects.exclude(pk=self.instance.id).filter(username=data.get('username')).exists():
                raise serializers.ValidationError({"username": ["A user with that username already exists."]})
            if User.objects.exclude(pk=self.instance.id).filter(email=data.get('email')).exists():
                raise serializers.ValidationError({"email": ["A user with that email already exists."]})

            if data.get('password'):
                """Change Password"""
                self.instance.set_password(data.pop('password'))
                self.instance.save()
                value = collections.OrderedDict(data)

        else:
            """Register a new user"""
            if not data.get('username'):
                raise serializers.ValidationError({"username": ["This field is required."]})
            if not data.get('email'):
                raise serializers.ValidationError({"email": ["This field is required."]})
            if not data.get('password'):
                raise serializers.ValidationError({"password": ["This field is required."]})
            
            if User.objects.filter(username=data['username']).exists():
                raise serializers.ValidationError({"username": ["A user with that username already exists."]})
            if User.objects.filter(email=data['email']).exists():
                raise serializers.ValidationError({"email": ["A user with that email already exists."]})

        return super().validate(value)


    def create(self, validated_data):
        """Register a new user"""
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
        )
        return user

    class Meta:
        model = User
        fields = ['username', 'email', 'id', 'token', 'password', 'image', ]


class OTPSerializer(serializers.ModelSerializer):

    class Meta:
        model = OTP
        fields = ['email', 'otp', ]

    def validate(self, data):
        if not User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": ["No user with this email", ]})
        return data


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'

        