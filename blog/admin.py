from django.contrib import admin
from .models import BlogPost, BlogComment

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published', 'created_at', 'updated_at')
    list_filter = ('published', 'author', 'created_at')
    search_fields = ('title', 'content', 'author__user__username')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'parent', 'created_at', 'likes', 'dislikes', 'replies_count')
    list_filter = ('created_at', 'post')
    search_fields = ('content', 'user__username')
