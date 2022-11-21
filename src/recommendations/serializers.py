import posts
from django.contrib.auth import get_user_model
from django.http import request

from rest_framework import serializers

from .models import Ratings, Labels
from groups.models import GroupsMember

User = get_user_model()

class RatingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ratings
        fields = '__all__'


class LabelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Labels
        fields = '__all__'
