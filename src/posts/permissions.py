from groups.models import GroupsMember
from rest_framework.permissions import BasePermission
from posts.models import Post, PostImages, PostLike, PostComment

class hasPostField(BasePermission):
    """Is in the same group as the obj"""
    message = "Access denied"

    def has_permission(self, request, view):
        post = 0

        if request.method == "GET":
            if not request.GET.get('post'):
                self.message = "post field is required"
                return False
            post = request.GET.get('post')
        else:
            if not request.data.get('post'):
                self.message = "post field is required"
                return False
            post = request.data.get('post')


class hasGroup_PostExists_UserBelongToPostGroup(BasePermission):
    message = "Not Found"

    def has_permission(self, request, view):
        if request.method == "GET":
            if not request.GET.get('post'):
                self.message = "post field is required"
                return False
            post_id = request.GET.get('post')
        else:
            if not request.data.get('post'):
                self.message = "post field is required"
                return False
            post_id = request.data.get('post')
            
        if not Post.objects.filter(pk=post_id).exists():
            return False

        post = Post.objects.get(pk=post_id)
        # Allowing only one user in a single group (SINGLEUSERCONSTRAINT)
        for group_member in GroupsMember.objects.filter(user=request.user):
            if group_member:
                self.message = "Permission Denied"
                if post.group == group_member.group:
                    return True

        return False
