from django.urls import path
from .views import (
    Posts, PostDetail,
    Comments, CommentDetail, PostComments, CommentDeleteByModerator, CommentDeleteByOwner
)

urlpatterns = [
    path('posts/', Posts.as_view(), name='blogpost-list'),
    path('posts/<int:pk>/', PostDetail.as_view(), name='blogpost-detail'),
    path('posts/<int:pk>/comments/', PostComments.as_view(), name='blogpost-comments'),
    path('comments/', Comments.as_view(), name='blogcomment-list'),
    path('comments/<int:pk>/', CommentDetail.as_view(), name='blogcomment-detail'),
    path('comments/<int:pk>/moderator-delete/', CommentDeleteByModerator.as_view(), name='moderator_comment_delete'),
    path('comments/<int:pk>/delete/', CommentDeleteByOwner.as_view(), name='owner_comment_delete'),
]
