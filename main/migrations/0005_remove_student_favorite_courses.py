# Generated by Django 5.1.2 on 2025-05-23 21:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_student_favorite_courses'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='favorite_courses',
        ),
    ]
