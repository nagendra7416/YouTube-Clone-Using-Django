# Generated by Django 4.1.7 on 2023-08-13 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0054_alter_video_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='gif',
            field=models.ImageField(blank=True, null=True, upload_to='gifs/'),
        ),
    ]
