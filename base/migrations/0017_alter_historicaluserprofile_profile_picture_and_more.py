# Generated by Django 5.0 on 2024-01-04 12:43

import base.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0016_alter_historicaluserprofile_profile_picture_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaluserprofile',
            name='profile_picture',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to=base.models.profile_picture_path),
        ),
    ]
