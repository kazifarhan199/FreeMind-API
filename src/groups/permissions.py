from groups.models import GroupsMember
from rest_framework.permissions import BasePermission

class IsInGroup(BasePermission):
    message = "Access denied"

    def has_permission(self, request, view):
        group = GroupsMember.objects.filter(user=request.user)
        if not group.exists():
            return False
        return True