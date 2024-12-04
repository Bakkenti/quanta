# Generated by Django 5.1.2 on 2024-12-03 19:50

import django.db.models.deletion
import django_ckeditor_5.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_rename_title_module_module_lesson_uploaded_video_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='comment_text',
            new_name='text',
        ),
        migrations.RemoveField(
            model_name='course',
            name='students_count',
        ),
        migrations.AlterField(
            model_name='lesson',
            name='content',
            field=django_ckeditor_5.fields.CKEditor5Field(blank=True),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='course',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='myapp.course'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='module',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='myapp.module'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='short_description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='uploaded_video',
            field=models.FileField(blank=True, null=True, upload_to='lesson_videos/'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='video_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]