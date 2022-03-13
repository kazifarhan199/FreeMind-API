from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from groups.models import GroupsMember
from groups.permissions import IsInGroup
from .pagination import PostPageNumberPagination, PostPageNumberPagination1000
from .models import Post, PostComment, PostLike
from . import serializers
from . import permissions


class PostCreateView(APIView):
    permission_classes = (IsAuthenticated, IsInGroup, )

    def post(self, request):
        data = {}
        data['image'] = request.data['images']
        data['title'] = request.data['title']

        data['user'] = request.user.id
        data['group'] = GroupsMember.objects.filter(user=request.user).first().group.id
        print(request.POST)
        serializer = serializers.PostSerializer(data=data, context={'request':request},)
        if serializer.is_valid():
            post = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostListView(ListAPIView):
    permission_classes = (IsAuthenticated, IsInGroup, )
    serializer_class = serializers.PostSerializer
    pagination_class = PostPageNumberPagination
    
    def get_queryset(self):
        queryset = Post.objects.filter(group=GroupsMember.objects.filter(user=self.request.user).first().group)
        return queryset.order_by('-created_on')


class PostDetailView(APIView):
    http_method_names = ('get', )
    permission_classes = (IsAuthenticated, permissions.hasGroup_PostExists_UserBelongToPostGroup, )

    def get(self, request):
            # Allowing only one user in a single group (SINGLEUSERCONSTRAINT)
        if Post.objects.filter(
            group = GroupsMember.objects.filter(user=request.user).first().group,
            pk = request.GET.get('post'),
        ).exists():
            serializer = serializers.PostSerializer(
                Post.objects.get(
                    # Allowing only one user in a single group (SINGLEUSERCONSTRAINT)
                    group = GroupsMember.objects.filter(user=request.user).first().group,
                    pk = request.GET.get('post'),
                ),
                context={'request':request},
            )
            return Response(serializer.data)
        else:
            return Response({'post':["Post not fount"]}, status=status.HTTP_404_NOT_FOUND)   


class PostDeleteView(APIView):
    http_method_names = ('delete', )
    permission_classes = (IsAuthenticated, permissions.hasGroup_PostExists_UserBelongToPostGroup, )

    def delete(self, request):
        Post.objects.get(pk=request.data.get('post'), user=request.user).delete()
        return Response({'detail': ["Post deleted.", ]}, status=status.HTTP_202_ACCEPTED)


class PostLikesListView(ListAPIView):
    permission_classes = (IsAuthenticated, permissions.hasGroup_PostExists_UserBelongToPostGroup, )
    serializer_class = serializers.PostLikeSerializer
    pagination_class = PostPageNumberPagination1000
    
    def get_queryset(self):
        queryset = PostLike.objects.filter(
                post = Post.objects.get(pk=self.request.GET.get('post'))
            )
        return queryset.order_by('-id')

class PostLikeView(APIView):
    permission_classes = (IsAuthenticated, permissions.hasGroup_PostExists_UserBelongToPostGroup, )


    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id        
        serializer = serializers.PostLikeSerializer(data=data, context={'request':request},)
        if serializer.is_valid():
            post = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        if not PostLike.objects.filter(
            post=Post.objects.get(pk=request.data.get('post')), 
            user=request.user,
        ).exists():
            return Response({"like": ["Like not found."]}, status=status.HTTP_404_NOT_FOUND)

        PostLike.objects.filter(
            user=request.user, 
            post=Post.objects.get(
                pk=request.data.get('post'), 
                group=GroupsMember.objects.filter(user=request.user).first().group
            )
        ).delete()
        return Response({'detail': ["like removed.", ]}, status=status.HTTP_202_ACCEPTED)


class PostCommentListView(ListAPIView):
    permission_classes = (IsAuthenticated, permissions.hasGroup_PostExists_UserBelongToPostGroup, )
    serializer_class = serializers.PostCommentSerializer
    pagination_class = PostPageNumberPagination1000
    
    def get_queryset(self):
        queryset = PostComment.objects.filter(
                post = Post.objects.get(pk=self.request.GET.get('post'))
            )
        return queryset.order_by('-created_on')

class PostCommentView(APIView):
    permission_classes = (IsAuthenticated, permissions.hasGroup_PostExists_UserBelongToPostGroup, )

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = serializers.PostCommentSerializer(data=data, context={'request':request},)
        if serializer.is_valid():
            post = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        if not request.data.get('comment'):
            return Response({"comment": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
        if not PostComment.objects.filter(
            post=Post.objects.get(pk=request.data.get('post')), 
            user=request.user,
            pk=request.data.get('comment'),
        ).exists():
            return Response({"comment": ["Comment not found."]}, status=status.HTTP_404_NOT_FOUND)

        PostComment.objects.filter(
            pk=request.data.get('comment'),
            user=request.user, 
            post=Post.objects.get(
                pk=request.data.get('post'), 
                group=GroupsMember.objects.filter(user=request.user).first().group
            )
        ).delete()
        return Response({'detail': ["Comment removed.", ]}, status=status.HTTP_202_ACCEPTED)


class CommentFeedbackView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = serializers.CommentFeedbackSerializer(data=data, context={'request':request},)
        if serializer.is_valid():
            feedback = serializer.save()
            c = PostComment.objects.get(pk=request.data['comment'])
            c.need_feadback = False
            c.save()            
            print(PostComment.objects.get(pk=request.data['comment']).need_feadback)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)