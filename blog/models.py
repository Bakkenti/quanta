from django.db import models
from main.models import Author
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.auth.models import User

class BlogPost(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='blog_posts')
    title = models.CharField(max_length=255)
    content = CKEditor5Field(config_name='default', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} — {self.author.user.username}"


class BlogComment(models.Model):
    post = models.ForeignKey(
        'blog.BlogPost',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    content = models.TextField()
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    likes = models.PositiveIntegerField(
        default=0
    )
    dislikes = models.PositiveIntegerField(
        default=0
    )
    replies_count = models.PositiveIntegerField(
        default=0
    )

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        if self.parent:
            return f"Reply from {self.user.username} to {self.parent.id}'s comment on post '{self.post.title}'"
        return f"Comment from {self.user.username} on post '{self.post.title}'"