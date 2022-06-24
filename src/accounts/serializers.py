import collections
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import OTP, Device, Profile
from groups.models import Groups, GroupsMember

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False, write_only=True)
    email = serializers.EmailField(required=False)
    gid = serializers.SerializerMethodField('get_gid', read_only=True)
    img_obj = serializers.ImageField(allow_null=True, required=False, write_only=True)
    bio = serializers.SerializerMethodField('get_bio', read_only=True)
    bio_obj = serializers.CharField(write_only=True)

    def get_bio(self, obj):
        return Profile.objects.get(user=obj).bio

    def get_gid(self, obj):
        if GroupsMember.objects.filter(user=obj).exists():
            return GroupsMember.objects.filter(user=obj).first().id
        else:
            return 0


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

            if data.get('bio_obj'):
                """Change bio"""
                p = Profile.objects.get(user=self.instance)
                p.bio = data.get('bio_obj')
                p.save()

        else:
            """Register a new user"""
            if not data.get('username'):
                raise serializers.ValidationError({"username": ["Username field is required."]})
            if not data.get('email'):
                raise serializers.ValidationError({"email": ["Email field is required."]})
            if not data.get('password'):
                raise serializers.ValidationError({"password": ["password field is required."]})
            
            if User.objects.filter(username=data['username']).exists():
                raise serializers.ValidationError({"username": ["A user with that username already exists."]})
            if User.objects.filter(email=data['email']).exists():
                raise serializers.ValidationError({"email": ["A user with that email already exists."]})

        return super().validate(value)

    def update(self, instance, validated_data): 
        if validated_data.get('img_obj', False):
            instance.profile.image = validated_data.get('img_obj', instance.profile.image)
            instance.profile.save()
        return super().update(instance, validated_data)

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
        fields = ['username', 'email', 'id', 'token', 'password', 'image', 'gid', 'img_obj', 'bio', 'bio_obj']


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

        