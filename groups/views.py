from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Groups, GroupsMember, User
from . import serializers

User = get_user_model()

class GroupsView(APIView):
    serializer_class = serializers.GroupsSerializer

    def get(self, request):
        group = Groups.objects.filter(user=request.user)
        serializer = self.serializer_class(group, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = self.serializer_class(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        # Allowing only one user in a single group (SINGLEUSERCONSTRAINT)
        serializer = self.serializer_class(data=data, instance=Groups.objects.filter(user=request.user).first())
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GroupsMemberView(APIView):
    serializer_class = serializers.GroupsMemberSerializer

    def post(self, request):
        serializer = serializers.GroupsMemberSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        email = request.data.get('email')
        if not email:
            return Response({"email": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(email=email).exists():
            return Response({"email": ["User with this email does not exists."]}, status=status.HTTP_400_BAD_REQUEST)
    
        if not GroupsMember.objects.filter(user=User.objects.get(email=email)).exists():
          return Response({"email": ["User with this email does not exists in the group."]}, status=status.HTTP_400_BAD_REQUEST)

        # Change to take group id from user (SINGLEUSERCONSTRAINT)
        if not GroupsMember.objects.filter(user=user).exists():
            return Response({"group": ["Access Denied."]}, status=status.HTTP_400_BAD_REQUEST)
    
        group=GroupsMember.objects.filter(user=user).first().group.id
        if not group:
        
            return Response({"group": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
        #
        if not Groups.objects.filter(pk=group).exists():
            """Group does not exists"""
            return Response({"group": ["No group found."]}, status=status.HTTP_400_BAD_REQUEST)
        
        if not GroupsMember.objects.filter(user=user, group_id=group).exists():
            """User who is removing is not in group"""
            return Response({"group": ["Access denied."]}, status=status.HTTP_400_BAD_REQUEST)
        

        GroupsMember.objects.filter(user=User.objects.get(email=email)).delete()
        return Response({'detail': ['User removed from the group']}, status=status.HTTP_202_ACCEPTED)


        