# Generated by Django 5.0 on 2023-12-28 07:15

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_alter_userprofile_ph_no_alter_userprofile_pin_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='ph_no',
            field=models.BigIntegerField(validators=[django.core.validators.MinLengthValidator(limit_value=10), django.core.validators.MaxLengthValidator(limit_value=10)]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='pin',
            field=models.BigIntegerField(validators=[django.core.validators.MinLengthValidator(limit_value=6), django.core.validators.MaxLengthValidator(limit_value=6)]),
        ),
    ]