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
            

class isinGroup(BasePermission):
    message = "Access denied"

    def has_permission(self, request, view):
        group = GroupsMember.objects.filter(user=request.user)
        if not group.exists():
            return False
        return True


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
        group_member = GroupsMember.objects.filter(user=request.user).first()
        
        if not group_member:
            self.message = "Permission Denied"
            return False

        if not post.group == group_member.group:
            return False

        return True
