from rest_framework import serializers
from .models import BlogPost, BlogComment


class BlogPostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.user.username', read_only=True)

    class Meta:
        model = BlogPost
        fields = [
            'id', 'author_username', 'title', 'content',
            'created_at', 'updated_at', 'published', 'image', 'views'
        ]

class BlogCommentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = BlogComment
        fields = [
            'id', 'post', 'parent', 'user', 'username',
            'content', 'created_at', 'likes', 'dislikes', 'replies_count', 'replies'
        ]

    def get_username(self, obj):
        if obj.user:
            return obj.user.username
        return "Deleted User"

    def get_replies(self, obj):
        qs = obj.replies.all().order_by('created_at')
        return BlogCommentSerializer(qs, many=True).data

