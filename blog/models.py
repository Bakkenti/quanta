from django.db import models
from main.models import Author
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.auth.models import User

class BlogPost(models.Model):
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='blog_posts',
        verbose_name='Автор'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Заголовок'
    )
    content = CKEditor5Field(
        config_name='default',
        blank=True,
        null=True,
        verbose_name='Содержимое'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлено'
    )
    published = models.BooleanField(
        default=False,
        verbose_name='Опубликован'
    )
    image = models.ImageField(
        upload_to='blog_images/',
        blank=True,
        null=True,
        verbose_name='Изображение (обложка)'
    )

    class Meta:
        verbose_name = 'Блог-пост'
        verbose_name_plural = 'Блог-посты'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} — {self.author.user.username}"


class BlogComment(models.Model):
    post = models.ForeignKey(
        'blog.BlogPost',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies',
        verbose_name='Родительский комментарий'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    avatar = models.ImageField(
        upload_to='comment_avatars/',
        null=True,
        blank=True,
        verbose_name='Аватарка'
    )
    content = models.TextField(
        verbose_name='Содержимое'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Когда написан'
    )
    likes = models.PositiveIntegerField(
        default=0,
        verbose_name='Лайки'
    )
    dislikes = models.PositiveIntegerField(
        default=0,
        verbose_name='Дизлайки'
    )
    replies_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество ответов'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        if self.parent:
            return f"Ответ от {self.user.username} к комментарию {self.parent.id} на пост '{self.post.title}'"
        return f"Комментарий от {self.user.username} к посту '{self.post.title}'"