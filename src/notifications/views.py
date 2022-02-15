from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Notification
from .serializers import NotificationSerializer

User = get_user_model()

class NotificationListView(APIView):
    serializer_class = NotificationSerializer
    model = Notification

    def get(self, request):
        queryset = self.model.objects.filter(
            user=request.user
        ).order_by('-created_on')
        data = {"notifications": NotificationSerializer(queryset, many=True).data}
        return Response(data)

    def post(self, request):
        if not request.data.get('id'):
            return Response({"detail":"Field id is required"}, status=status.HTTP_400_BAD_REQUEST)
        if Notification.objects.filter(user=request.user, pk=request.data.get('id')).exists():
            no = Notification.objects.get(user=request.user, pk=request.data.get('id'))
            no.seen = True
            no.save()
            return Response({"detail":"Done"})
        return Response({"detail":"Notification not found"}, status=status.HTTP_404_NOT_FOUND)

class NotificationHowMany(APIView):
    def get(self, request):
        queryset = Notification.objects.filter(
            user=request.user, seen=False
        )
        data = {"how-many": len(queryset)}
        return Response(data)