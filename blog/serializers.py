from rest_framework import serializers
from .models import BlogPost, BlogComment


class BlogPostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.user.username', read_only=True)

    class Meta:
        model = BlogPost
        fields = [
            'id', 'author_username', 'title', 'content',
            'created_at', 'updated_at', 'published', 'image'
        ]

class BlogCommentSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = BlogComment
        fields = [
            'id', 'post', 'parent', 'user', 'user_username', 'avatar',
            'content', 'created_at', 'likes', 'dislikes', 'replies_count', 'replies'
        ]

    def get_replies(self, obj):
        qs = obj.replies.all().order_by('created_at')
        return BlogCommentSerializer(qs, many=True).data
