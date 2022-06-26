from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.generics import ListAPIView, CreateAPIView

from accounts.serializers import UserSerializer
from .models import Groups, GroupsMember, User
from . import serializers
from . import permissions
from posts.pagination import PostPageNumberPagination1000

User = get_user_model()

class GroupListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.GroupsSerializer
    pagination_class = PostPageNumberPagination1000
    
    def get_queryset(self):
        gms = [gm.group.id for gm in GroupsMember.objects.filter(user=self.request.user, group__gtype='Default')]
        for gm in GroupsMember.objects.filter(user=self.request.user, group__gtype='Channel'):
            if gm.user == gm.group.user:
                gms.append(gm.group.id)
        queryset = Groups.objects.filter(
                pk__in=gms
            )
        return queryset.order_by('-id')

class GroupsView(APIView):
    serializer_class = serializers.GroupsSerializer
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        # Allowing only one user in a single group (SINGLEUSERCONSIsInGroupTRAIN)
        if not request.GET.get('group'):
            '''group field is provided'''
            return Response({"group": ["Group field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        if not Groups.objects.filter(pk=request.GET['group']).exists():
            '''Group does not exists'''
            return Response({"group": ["Group does not exists."]}, status=status.HTTP_400_BAD_REQUEST)

        if not GroupsMember.objects.filter(user=request.user, group=Groups.objects.get(pk=request.GET['group'])).exists():
            '''User not present in group'''
            return Response({"user": ["User not part of group."]}, status=status.HTTP_400_BAD_REQUEST)

        group = GroupsMember.objects.get(user=request.user, group=Groups.objects.get(pk=request.GET['group'])).group
        serializer = self.serializer_class(group, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        data = request.data.copy()
        data['user'] = request.user.id

        if not request.GET.get('group'):
            '''group field is provided'''
            return Response({"group": ["Group field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        if not Groups.objects.filter(pk=request.GET['group']).exists():
            '''Group does not exists'''
            return Response({"group": ["Group does not exists."]}, status=status.HTTP_400_BAD_REQUEST)

        if not GroupsMember.objects.filter(user=request.user, group=Groups.objects.get(pk=request.GET['group'])).exists():
            '''User not present in group'''
            return Response({"user": ["User not part of group."]}, status=status.HTTP_400_BAD_REQUEST)

        group = GroupsMember.objects.get(user=request.user, group=Groups.objects.get(pk=request.GET['group'])).group

        serializer = self.serializer_class(data=data, instance=group , context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupsCreateView(APIView):
    serializer_class = serializers.GroupsSerializer

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = self.serializer_class(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupsMemberView(APIView):
    serializer_class = serializers.GroupsMemberSerializer
    permission_classes = (IsAuthenticated, permissions.IsInGroup)

    def post(self, request): 
        serializer = serializers.GroupsMemberSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        serializer = serializers.GroupsMemberSerializer(data=request.data, context={'request': request})

        gm = GroupsMember.objects.get(user=User.objects.get(email=request.data.get('email')), group__gtype='Default', group=Groups.objects.get(pk=request.GET['group']))
        gm.delete()
        return Response({'detail': ['User removed from the group']}, status=status.HTTP_202_ACCEPTED)


class GroupsChannelView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        groups = Groups.objects.filter(gtype='Channel')
        serializer = serializers.GroupsSerializer(groups, context={'request': request}, many=True)
        return Response({'results':serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        if not Groups.objects.filter(id=request.data['group'], gtype='Channel').exists():
            return Response({'detail': ['Channel not found']}, status=status.HTTP_404_NOT_FOUND) 
        elif (GroupsMember.objects.filter(group=Groups.objects.get(id=request.data['group'], gtype='Channel'), user=request.user)).exists():
            return Response({'detail': ['User already following channel']}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                channel = Groups.objects.get(id=request.data['group'], gtype='Channel')
                GroupsMember.objects.create(user=request.user, group=channel)
                return Response({'detail': ['User Added']}, status=status.HTTP_201_CREATED)
            except:
                return Response({'detail': ['Unable to add user to group please contact admin']}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        if not Groups.objects.filter(id=request.data['group'], gtype='Channel').exists():
            return Response({'detail': ['Channel not found']}, status=status.HTTP_404_NOT_FOUND) 
        elif (GroupsMember.objects.filter(group=Groups.objects.get(id=request.data['group'], gtype='Channel'), user=request.user)).exists():
            try:
                channel = Groups.objects.get(id=request.data['group'], gtype='Channel')
                GroupsMember.objects.get(user=request.user, group=channel).delete()
                return Response({'detail': ['User Removed']}, status=status.HTTP_202_ACCEPTED)
            except:
                return Response({'detail': ['Unable to remove user to group please contact admin']}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'detail': ['User already removed from channel']}, status=status.HTTP_404_NOT_FOUND)