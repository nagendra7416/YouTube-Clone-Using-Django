# Generated by Django 3.2.7 on 2022-10-30 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20221030_1442'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='history',
            name='post',
        ),
        migrations.AddField(
            model_name='history',
            name='post',
            field=models.ManyToManyField(related_name='post', to='app.Video'),
        ),
    ]
