from rest_framework import serializers
from .models import Video
from django.contrib.auth.models import User
class VideoSerializer(serializers.ModelSerializer):
    published = serializers.DateTimeField(format="%d %B, %Y")
    class Meta:
        model = Video
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.author.channeluser.channelname
        representation['subs'] = instance.author.channeluser.subscribers.all().count()
        representation['views'] = instance.views.all().count()
        representation['liked'] = instance.liked.all().count()
        representation['image'] = "http://localhost:8000"+instance.image.url
        representation['video'] = "http://localhost:8000"+instance.video.url
        representation['channelimg'] = "http://localhost:8000"+instance.author.channeluser.channelimg.url

        return representation

class UserSerializer(serializers.ModelSerializer):
    class Meta: 
        model = User
        fields = '__all__'

        def to_repren(self, instance):
            context = super().to_repren(instance)
            context['username'] = instance.username

            return context
            