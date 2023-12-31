# Generated by Django 4.1.7 on 2023-08-14 08:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0060_rename_video_file_video_video'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoryVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('his_user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('his_video', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.video')),
            ],
        ),
    ]
