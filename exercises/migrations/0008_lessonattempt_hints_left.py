# Generated by Django 5.1.2 on 2025-06-11 01:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exercises', '0007_hintrequestlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessonattempt',
            name='hints_left',
            field=models.PositiveIntegerField(default=3),
        ),
    ]
