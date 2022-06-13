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

User = get_user_model()

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

class GroupsView(APIView):
    serializer_class = serializers.GroupsSerializer
    permission_classes = (IsAuthenticated, permissions.IsInGroup)

    def get(self, request):
        # Allowing only one user in a single group (SINGLEUSERCONSTRAINT)
        group = GroupsMember.objects.filter(user=request.user).first().group
        serializer = self.serializer_class(group, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        # Allowing only one user in a single group (SINGLEUSERCONSTRAINT)
        serializer = self.serializer_class(data=data, instance=GroupsMember.objects.filter(user=request.user).first().group , context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupsMemberView(APIView):
    serializer_class = serializers.GroupsMemberSerializer
    permission_classes = (IsAuthenticated, permissions.IsInGroup)

    def get(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"email": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        if GroupsMember.objects.filter(user__email=email).exists():
            return Response({'detail': ['User unavailable']}, status=status.HTTP_404_NOT_FOUND)
        else:
            if User.objects.filter(email=email).exists():
                return Response(UserSerializer(User.objects.get(email=email)).data)
            else:
                return Response({'detail': ['User unavailable']}, status=status.HTTP_404_NOT_FOUND)



    def post(self, request): 
        serializer = serializers.GroupsMemberSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        instance_user = request.user
        email = request.data.get('email')
        if not email:
            return Response({"email": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(email=email).exists():
            return Response({"email": ["User with this email does not exists."]}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(email=email)

        # Change to take group id from user (SINGLEUSERCONSTRAINT)
        if not GroupsMember.objects.filter(user=instance_user).exists():
            return Response({"group": ["Access Denied."]}, status=status.HTTP_400_BAD_REQUEST)

        instance_usergroup = GroupsMember.objects.get(user=instance_user).group
        #

        if not GroupsMember.objects.filter(user=user, group=instance_usergroup).exists():
          return Response({"email": ["User with this email does not exists in the group."]}, status=status.HTTP_400_BAD_REQUEST)

        GroupsMember.objects.filter(user=user).delete()
        return Response({'detail': ['User removed from the group']}, status=status.HTTP_202_ACCEPTED)


class GroupsChannelView(APIView):

    def get(self, request):
        # Allowing only one user in a single group (SINGLEUSERCONSTRAINT)
        groups = Groups.objects.filter(gtype='Channel')
        serializer = serializers.GroupsSerializer(groups, context={'request': request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not Groups.objects.filter(id=request.data['group'], gtype='Channel').exists():
            return Response({'detail': ['Channel not found']}, status=status.HTTP_404_NOT_FOUND) 
        elif (GroupsMember.objects.filter(group=Groups.objects.get(id=request.data['group'], gtype='Channel'), user=request.user)).exists():
            return Response({'detail': ['User already following channel']}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                channel = Groups.objects.get(id=request.data['group'], gtype='Channel')
                GroupsMember.objects.create(user=request.user, group=channel)
                return Response({'detail': ['User Added']}, status=status.HTTP_200_OK)
            except:
                return Response({'detail': ['Unable to add user to group please contact admin']}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        if not Groups.objects.filter(id=request.data['group'], gtype='Channel').exists():
            return Response({'detail': ['Channel not found']}, status=status.HTTP_404_NOT_FOUND) 
        elif (GroupsMember.objects.filter(group=Groups.objects.get(id=request.data['group'], gtype='Channel'), user=request.user)).exists():
            try:
                channel = Groups.objects.get(id=request.data['group'], gtype='Channel')
                GroupsMember.objects.get(user=request.user, group=channel).delete()
                return Response({'detail': ['User Removed']}, status=status.HTTP_200_OK)
            except:
                return Response({'detail': ['Unable to remove user to group please contact admin']}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'detail': ['User already following channel']}, status=status.HTTP_404_NOT_FOUND)