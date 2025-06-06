# Generated by Django 5.1.2 on 2025-06-01 18:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exercises', '0005_alter_exercise_description_alter_exercise_type_and_more'),
        ('main', '0011_author_is_journalist'),
    ]

    operations = [
        migrations.CreateModel(
            name='LessonAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('answers', models.JSONField()),
                ('score', models.IntegerField(default=0)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.lesson')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.student')),
            ],
        ),
        migrations.DeleteModel(
            name='ExerciseAttempt',
        ),
    ]
