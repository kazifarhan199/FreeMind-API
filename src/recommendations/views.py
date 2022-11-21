from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework import status

from posts.pagination import PostPageNumberPagination1000
from . import serializers, models


class QuestionsListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.LabelsSerializer
    pagination_class = PostPageNumberPagination1000
    
    def get_queryset(self):
        if len(models.Ratings.objects.filter(user=self.request.user)) > 20:
            queryset = models.Labels.objects.filter(is_label=False, is_coupuled=False).order_by('?')[:1]
        else:
            queryset = models.Labels.objects.filter(is_label=False, is_coupuled=False).order_by('-id')
        return queryset 

class QuestionsCopuledListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.LabelsSerializer
    pagination_class = PostPageNumberPagination1000
    
    def get_queryset(self):
        if len(models.Ratings.objects.filter(user=self.request.user)) > 20:
            queryset = models.Labels.objects.filter(is_label=False, is_coupuled=True).order_by('?')[:1]
        else:
            queryset = models.Labels.objects.filter(is_label=False, is_coupuled=True).order_by('-id')
        return queryset


class LabelsListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.LabelsSerializer
    pagination_class = PostPageNumberPagination1000
    
    def get_queryset(self):
        if len(models.Ratings.objects.filter(user=self.request.user)) > 20:
            queryset = models.Labels.objects.filter(is_label=True).order_by("?")[:3]
        else:
            queryset = models.Labels.objects.filter(is_label=True).order_by('?')[:15]
        return queryset

class LabelsCreateView(CreateAPIView):
    serializer_class = serializers.LabelsSerializer
 
class RecommendationsView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        data['is_active'] = True
        serializer = serializers.RatingsSerializer(data=data, context={'request':request},)
        if serializer.is_valid():
            for obj in models.Ratings.objects.filter(user=self.request.user, label=data['label'], is_active=True):
                obj.is_active = False
                obj.save()
            rating = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)