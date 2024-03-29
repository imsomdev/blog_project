# Generated by Django 5.0 on 2024-01-15 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0027_remove_blogcontent_tags_delete_tag'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='blogcontent',
            name='tags',
            field=models.ManyToManyField(blank=True, to='base.tag'),
        ),
    ]
