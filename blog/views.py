from rest_framework import generics
from .models import BlogPost, BlogComment
from .serializers import BlogPostSerializer, BlogCommentSerializer
from rest_framework.permissions import AllowAny


class Posts(generics.ListAPIView):
    queryset = BlogPost.objects.filter(published=True).order_by('-created_at')
    serializer_class = BlogPostSerializer
    permission_classes = [AllowAny]


class PostDetail(generics.RetrieveAPIView):
    queryset = BlogPost.objects.filter(published=True)
    serializer_class = BlogPostSerializer
    permission_classes = [AllowAny]


class Comments(generics.ListAPIView):  #/?page=number
    queryset = BlogComment.objects.all().order_by('-created_at')
    serializer_class = BlogCommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return BlogComment.objects.filter(parent=None).order_by('-created_at')

class PostComments(generics.ListAPIView):
    serializer_class = BlogCommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        post_id = self.kwargs['pk']
        post = BlogPost.objects.get(pk=post_id)
        return BlogComment.objects.filter(post=post, parent=None).order_by('created_at')


class CommentDetail(generics.RetrieveAPIView):
    queryset = BlogComment.objects.all()
    serializer_class = BlogCommentSerializer
    permission_classes = [AllowAny]
