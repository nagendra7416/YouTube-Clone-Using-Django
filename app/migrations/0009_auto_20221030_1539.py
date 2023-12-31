# Generated by Django 3.2.7 on 2022-10-30 10:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0008_auto_20221030_1519'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='history',
            name='vid',
        ),
        migrations.AddField(
            model_name='history',
            name='video_id',
            field=models.CharField(blank=True, max_length=10000, null=True),
        ),
        migrations.AlterField(
            model_name='history',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
