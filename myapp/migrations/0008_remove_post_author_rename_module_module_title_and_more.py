# Generated by Django 5.1.2 on 2025-01-11 22:35

import django.db.models.deletion
import myapp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_user_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='author',
        ),
        migrations.RenameField(
            model_name='module',
            old_name='module',
            new_name='title',
        ),
        migrations.RemoveField(
            model_name='course',
            name='author',
        ),
        migrations.RemoveField(
            model_name='course',
            name='students',
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='content',
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='course',
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='short_description',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_author',
        ),
        migrations.AddField(
            model_name='user',
            name='is_student',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='author',
            name='about',
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='author',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/'),
        ),
        migrations.AddField(
            model_name='author',
            name='birthday',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='author',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1),
        ),
        migrations.AddField(
            model_name='author',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='author',
            name='user',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='author', to='myapp.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lesson',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lesson',
            name='duration',
            field=models.CharField(default=1, help_text="Enter duration (e.g., '25:32')", max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='student',
            name='user',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='student', to='myapp.user'),
            preserve_default=False,
        ),

        migrations.RemoveField(
            model_name='author',
            name='published_courses',
        ),
        migrations.AlterField(
            model_name='course',
            name='course_image',
            field=models.ImageField(blank=True, null=True, upload_to='course_images/'),
        ),
        migrations.AlterField(
            model_name='course',
            name='duration',
            field=models.CharField(help_text="e.g., '4 weeks'", max_length=20, validators=[myapp.models.validate_course_duration]),
        ),
        migrations.AlterField(
            model_name='course',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='course',
            name='level',
            field=models.CharField(choices=[('all', 'All Levels'), ('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('expert', 'Expert')], default='all', max_length=50),
        ),
        migrations.AlterField(
            model_name='course',
            name='rating',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='myapp.module'),
        ),
        migrations.AlterField(
            model_name='module',
            name='duration',
            field=models.CharField(help_text="Enter duration (e.g., '2 hours' or '15 minutes')", max_length=20, validators=[myapp.models.validate_module_duration]),
        ),
        migrations.AlterField(
            model_name='module',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.RemoveField(
            model_name='student',
            name='subscribed_courses',
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
        migrations.DeleteModel(
            name='Post',
        ),
        migrations.AddField(
            model_name='author',
            name='published_courses',
            field=models.ManyToManyField(blank=True, to='myapp.course'),
        ),
        migrations.AddField(
            model_name='student',
            name='subscribed_courses',
            field=models.ManyToManyField(blank=True, to='myapp.course'),
        ),
    ]
