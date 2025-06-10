from rest_framework import generics
from .models import BlogPost, BlogComment
from django.db import models
from .serializers import BlogPostSerializer, BlogCommentSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class Posts(generics.ListAPIView):
    queryset = BlogPost.objects.filter(published=True).order_by('-created_at')
    serializer_class = BlogPostSerializer
    permission_classes = [AllowAny]


class PostDetail(generics.RetrieveAPIView):
    queryset = BlogPost.objects.filter(published=True)
    serializer_class = BlogPostSerializer

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        client_ip = self.get_client_ip(request)
        cache_key = f"viewed_post_{instance.pk}_{client_ip}"
        from django.core.cache import cache

        if not cache.get(cache_key):
            instance.views = models.F('views') + 1
            instance.save(update_fields=['views'])
            cache.set(cache_key, True, 60 * 60 * 6)

        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class Comments(generics.ListAPIView):  #/?page=number
    queryset = BlogComment.objects.all().order_by('-created_at')
    serializer_class = BlogCommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return BlogComment.objects.filter(parent=None).order_by('-created_at')

class PostComments(generics.ListCreateAPIView):
    serializer_class = BlogCommentSerializer

    permission_classes = [AllowAny]

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

class CommentDeleteByModerator(generics.DestroyAPIView):
    queryset = BlogComment.objects.all()
    serializer_class = BlogCommentSerializer

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

class CommentDeleteByOwner(generics.DestroyAPIView):
    queryset = BlogComment.objects.all()
    serializer_class = BlogCommentSerializer

    def delete(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.user != request.user:
            return Response({"error": "You can delete only your own comments."}, status=403)
        return super().delete(request, *args, **kwargs)
