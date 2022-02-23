from django.contrib import admin
from .models import Post, PostImages, PostLike, PostComment, CommentFeedback

admin.site.register(Post)
admin.site.register(PostImages)
admin.site.register(PostLike)
admin.site.register(PostComment)
admin.site.register(CommentFeedback)