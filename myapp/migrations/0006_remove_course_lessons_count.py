# Generated by Django 5.1.2 on 2024-12-03 20:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_alter_student_password'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='lessons_count',
        ),
    ]
