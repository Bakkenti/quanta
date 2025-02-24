# Generated by Django 5.1.2 on 2025-02-23 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0010_rename_number_module_module_id_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='lesson',
            unique_together={('module', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='module',
            unique_together={('course', 'module')},
        ),
        migrations.AlterField(
            model_name='lesson',
            name='lesson_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='module',
            name='module_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
