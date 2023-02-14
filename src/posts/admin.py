from django.contrib import admin
from .models import Post, PostImages, PostLike, PostComment, CommentFeedback

class PostAdmin(admin.ModelAdmin):
    search_fields = ['user__username','title']

admin.site.register(Post, PostAdmin)
admin.site.register(PostImages)
admin.site.register(PostLike)
admin.site.register(PostComment)
admin.site.register(CommentFeedback)