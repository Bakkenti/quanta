from rest_framework import generics
from .models import BlogPost, BlogComment
from .serializers import BlogPostSerializer, BlogCommentSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


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

class PostComments(generics.ListCreateAPIView):
    serializer_class = BlogCommentSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        post_pk = self.kwargs['pk']
        return BlogComment.objects.filter(post__pk=post_pk, parent=None).order_by('created_at')

    def perform_create(self, serializer):
        post_pk = self.kwargs['pk']
        post = BlogPost.objects.get(pk=post_pk)
        serializer.save(post=post, user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        write_comment = {
            "allowed": request.user.is_authenticated,
            "message": (
                "Login required to leave a comment"
                if not request.user.is_authenticated else
                "You can leave a comment"
            ),
            "form_fields": {
                "content": "string",
                "parent": "optional id"
            }
        }
        return Response({
            "comments": serializer.data,
            "write_comment": write_comment
        })


class CommentDetail(generics.RetrieveAPIView):
    queryset = BlogComment.objects.all()
    serializer_class = BlogCommentSerializer
    permission_classes = [AllowAny]
