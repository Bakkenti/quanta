# Generated by Django 5.1.2 on 2025-05-18 19:10

import django.db.models.deletion
import django_ckeditor_5.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('main', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('slug', models.SlugField(max_length=255, unique=True, verbose_name='Слаг (URL)')),
                ('content', django_ckeditor_5.fields.CKEditor5Field(blank=True, null=True, verbose_name='Содержимое')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
                ('published', models.BooleanField(default=False, verbose_name='Опубликован')),
                ('image', models.ImageField(blank=True, null=True, upload_to='blog_images/', verbose_name='Изображение (обложка)')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_posts', to='main.author', verbose_name='Автор')),
            ],
            options={
                'verbose_name': 'Блог-пост',
                'verbose_name_plural': 'Блог-посты',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BlogComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='comment_avatars/', verbose_name='Аватарка')),
                ('content', models.TextField(verbose_name='Содержимое')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Когда написан')),
                ('likes', models.PositiveIntegerField(default=0, verbose_name='Лайки')),
                ('dislikes', models.PositiveIntegerField(default=0, verbose_name='Дизлайки')),
                ('replies_count', models.PositiveIntegerField(default=0, verbose_name='Количество ответов')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='blog.blogcomment', verbose_name='Родительский комментарий')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='blog.blogpost', verbose_name='Пост')),
            ],
            options={
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Комментарии',
                'ordering': ['created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='blogpost',
            index=models.Index(fields=['slug'], name='blog_blogpo_slug_361555_idx'),
        ),
    ]
