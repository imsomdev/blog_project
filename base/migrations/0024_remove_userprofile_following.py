# Generated by Django 5.0 on 2024-01-15 06:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0023_alter_userprofile_following'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='following',
        ),
    ]
