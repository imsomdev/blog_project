# Generated by Django 5.0 on 2024-01-23 09:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0035_remove_follow_created_at_remove_question_pub_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='choice',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='base.question'),
        ),
    ]
