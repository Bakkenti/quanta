# Generated by Django 5.1.2 on 2025-05-24 09:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_alter_student_gender'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgrammingLanguage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='language',
            field=models.ForeignKey(blank=True, help_text='Programming language for this exercise (required for code tasks)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exercises', to='main.programminglanguage'),
        ),
    ]
