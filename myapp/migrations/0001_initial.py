# Generated by Django 5.1.2 on 2024-10-19 07:13

import django.db.models.deletion
import myapp.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=101, unique=True)),
                ('password', models.CharField(max_length=100)),
                ('about', models.TextField(default='No information available.')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('comment_text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('course_image', models.ImageField(blank=True, null=True, upload_to='course_images/')),
                ('description', models.TextField()),
                ('duration', models.CharField(help_text="Enter duration (e.g., '3 weeks' or '1 day')", max_length=20, validators=[myapp.models.validate_course_duration])),
                ('students_count', models.IntegerField(default=0)),
                ('lessons_count', models.IntegerField(default=0)),
                ('level', models.CharField(choices=[('all', 'All Levels'), ('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('expert', 'Expert')], default='all', max_length=20)),
                ('rating', models.DecimalField(blank=True, decimal_places=1, default=0, max_digits=2, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='myapp.author')),
            ],
        ),
        migrations.AddField(
            model_name='author',
            name='course_list',
            field=models.ManyToManyField(blank=True, related_name='authored_courses', to='myapp.course'),
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('duration', models.CharField(max_length=20, validators=[myapp.models.validate_module_duration])),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modules', to='myapp.course')),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('video_url', models.URLField(blank=True, null=True)),
                ('short_description', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='myapp.course')),
                ('module', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='myapp.module')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('date_posted', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='myapp.author')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=100, unique=True)),
                ('password', models.CharField(max_length=120)),
                ('subscribed_courses', models.ManyToManyField(blank=True, to='myapp.course')),
            ],
        ),
    ]
