# Generated by Django 3.2.7 on 2022-11-03 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0024_channel_channeldescription'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='joined',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]