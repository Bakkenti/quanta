# Generated by Django 5.1.2 on 2025-06-07 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_certificate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certificate',
            name='hash_code',
            field=models.CharField(max_length=64),
        ),
    ]
