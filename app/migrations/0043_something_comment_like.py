# Generated by Django 3.2.7 on 2022-11-07 15:48

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0042_playlist_playlist_visibility'),
    ]

    operations = [
        migrations.AddField(
            model_name='something',
            name='comment_like',
            field=models.ManyToManyField(related_name='comment_like', to=settings.AUTH_USER_MODEL),
        ),
    ]
