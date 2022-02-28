from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework import status

from posts.pagination import PostPageNumberPagination1000
from . import serializers, models


class LabelsListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.LabelsSerializer
    pagination_class = PostPageNumberPagination1000
    
    def get_queryset(self):
        queryset = models.Labels.objects.all()
        return queryset

class LabelsCreateView(CreateAPIView):
    serializer_class = serializers.LabelsSerializer
 
class RecommendationsView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = serializers.RatingsSerializer(data=data, context={'request':request},)
        if serializer.is_valid():
            rating = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)