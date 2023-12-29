# Generated by Django 5.0 on 2023-12-28 07:12

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_alter_userprofile_ph_no_alter_userprofile_pin'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='ph_no',
            field=models.IntegerField(validators=[django.core.validators.MinLengthValidator(limit_value=10), django.core.validators.MaxLengthValidator(limit_value=10)]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='pin',
            field=models.IntegerField(validators=[django.core.validators.MinLengthValidator(limit_value=6), django.core.validators.MaxLengthValidator(limit_value=6)]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]