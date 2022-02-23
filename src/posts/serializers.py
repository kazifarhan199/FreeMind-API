import posts
from django.contrib.auth import get_user_model
from django.http import request

from rest_framework import serializers

from .models import Post, PostImages, PostLike, PostComment, CommentFeedback
from groups.models import GroupsMember

User = get_user_model()


class CommentFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentFeedback
        fields = '__all__'

    def validate(self, valid_data):
        if valid_data['user'] != valid_data['comment'].post.user:
            raise serializers.ValidationError({"user": ["You are not allowed to rate this comment."]})
        if valid_data['comment'].need_feadback == False:
            raise serializers.ValidationError({"user": ["You are not allowed to rate this comment."]})
        return super().validate(valid_data)

class PostImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PostImages
        fields = ['image_url', ]


class PostSerializer(serializers.ModelSerializer):
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    liked = serializers.SerializerMethodField('isLiked')

    def validate(self, valid_data):
        valid_data['user'] = self.context['request'].user
        # Allowing only one user in a single group (SINGLEUSERCONSTRAINT)
        if not self.context['request'].data.get('images'):
            """User who is add is not in group"""
            raise serializers.ValidationError({"images": ["This fiels is required."]})
        return super().validate(valid_data)

    def create(self, valid_data):
        post = super().create(valid_data)
        PostImages.objects.create(post=post, image=self.context['request'].data['images'])
        return post


    def isLiked(self, obj):
        request = self.context.get('request', None)
        user = request.user
        if PostLike.objects.filter(post=obj, user=user).exists():
            return True
        else:
            return False

    class Meta:
        model = Post
        fields = (
            'id',
            'group',
            'title',
            'username',
            'user_image',
            'comment_count',
            'like_count',
            'created_on',
            'updated_on',
            'images',
            'liked',
        )


class PostLikeSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField('get_username')
    userimage = serializers.SerializerMethodField('get_userimage')

    def get_username(self, obj):
        return obj.username()

    def get_userimage(self, obj):
        return obj.user_image()

    class Meta:
        model = PostLike
        fields = ['username', 'userimage', 'user', 'post']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('user', 'post'),
                message="Like already present."
            )
        ]

    def is_valid(self):
        if not (self.context['request'].data.get('post')):
            raise serializers.ValidationError({"post": ["This field is required."]}, code=400)

        if not Post.objects.filter(pk=self.context['request'].data['post']).exists():
            raise serializers.ValidationError({"post": ["Post Not found."]}, code=404)

        return super().is_valid()

    def validate(self, valid_data):
        request = self.context['request']
        valid_data['user'] = request.user

        # Allowing only one user in a single group (SINGLEUSERCONSTRAINT)
        group = GroupsMember.objects.filter(user=request.user).first().group.id
        post_group = Post.objects.get(pk=valid_data['post'].id).group.id

        if not group == post_group:
            """User who is add is not in group"""
            raise serializers.ValidationError({"group": ["Access denied."]})
        return super().validate(valid_data)


class PostCommentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField('get_username')
    userimage = serializers.SerializerMethodField('get_userimage')

    def get_username(self, obj):
        return obj.user.username

    def get_userimage(self, obj):
        return obj.user.image

    class Meta:
        model = PostComment
        fields = ["id", "text", "created_on", "need_feadback", "username", "userimage", 'post', ]


    def is_valid(self):
        if not (self.context['request'].data.get('post')):
            raise serializers.ValidationError({"post": ["This field is required."]}, code=400)

        if not Post.objects.filter(pk=self.context['request'].data['post']).exists():
            raise serializers.ValidationError({"post": ["Post Not found."]}, code=404)

        return super().is_valid()

    def validate(self, valid_data):
        request = self.context['request']
        valid_data['user'] = request.user

        # Allowing only one user in a single group (SINGLEUSERCONSTRAINT)
        group = GroupsMember.objects.filter(user=request.user).first().group.id
        post_group = Post.objects.get(pk=valid_data['post'].id).group.id

        if not group == post_group:
            """User who is add is not in group"""
            raise serializers.ValidationError({"group": ["Access denied."]})
        return super().validate(valid_data)