from django.urls import path
from .views import (
    Posts, PostDetail,
    Comments, CommentDetail, PostComments
)

urlpatterns = [
    path('posts/', Posts.as_view(), name='blogpost-list'),
    path('posts/<int:pk>/', PostDetail.as_view(), name='blogpost-detail'),
    path('posts/<int:pk>/comments/', PostComments.as_view(), name='blogpost-comments'),
    path('comments/', Comments.as_view(), name='blogcomment-list'),
    path('comments/<int:pk>/', CommentDetail.as_view(), name='blogcomment-detail'),
]
