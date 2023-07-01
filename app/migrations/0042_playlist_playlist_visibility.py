# Generated by Django 3.2.7 on 2022-11-07 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0041_playlist_playlist_videos'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='playlist_visibility',
            field=models.CharField(blank=True, choices=[('Public', 'Public'), ('Private', 'Private')], default='Public', max_length=255),
        ),
    ]