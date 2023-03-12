from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ['id','object_id', 'send_object', 'type', 'title', 'body', 'date_time', 'username', 'user_image']
        
