from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ['id','post', 'post_comment', 'post_like', 'created_on', 'username', 'user_image', 'seen', 'text', ]
        
