# Generated by Django 4.1.7 on 2023-08-13 16:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0058_channel_channelslug'),
    ]

    operations = [
        migrations.RenameField(
            model_name='video',
            old_name='video',
            new_name='video_file',
        ),
    ]
