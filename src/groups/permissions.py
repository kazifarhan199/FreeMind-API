from django.contrib.auth import get_user_model
from groups.models import Groups, GroupsMember
from rest_framework.permissions import BasePermission

User = get_user_model()

class IsInGroup(BasePermission):
    message = "Access denied"

    def has_permission(self, request, view):
        if not request.GET.get('group'):
            print('''group field is provided''')
            return False

        if not Groups.objects.filter(pk=request.GET['group']).exists():
            print('''Group does not exists''')
            return False

        if not GroupsMember.objects.filter(user=request.user, group=Groups.objects.get(pk=request.GET['group'])).exists():
            print('''User not present in group''')
            return False

        if not request.data.get('email'):
            print("email field not provided")
            return False

        user = None
        if User.objects.filter(email=request.data.get('email')).exists():
            user = User.objects.get(email=request.data.get('email'))
        elif User.objects.filter(username=request.data.get('email')).exists():
            user = User.objects.get(username=request.data.get('email'))
        if not user:
            return False

        if not GroupsMember.objects.filter(user=request.user, group=Groups.objects.get(pk=request.GET['group'])).exists():
            print('''User not present in group''')
            return False

        return True

