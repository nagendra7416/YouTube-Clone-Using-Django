from datetime import date
from multiprocessing import context
from urllib import response
from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from .forms import ChannelCreateForm, CommentForm
from .models import Channel, Notification, Video, Comment, something, Playlist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate
from django.db.models import Q
from .serializers import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models.expressions import Case, When
from django.views import View
import datetime
from django.forms.models import model_to_dict
import json
from django.core import serializers









class ReactView(APIView):
    def get(self, request):
        video = Video.objects.all().order_by("?")
        serializer = VideoSerializer(video, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

class UserView(APIView):
    def get(self, request):
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data)

class VideoView(APIView):
    def get_object(self, id):
        try: 
            return Video.objects.get(id=id)
        except Video.DoesNotExist:
            return Response("object requested does not exists", status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id):
        video = self.get_object(id)
        serializer = VideoSerializer(video)
        return Response(serializer.data)



def home(request):
    videos = Video.objects.filter(visibility='Public').all().order_by('?')
    for i in videos:
        if i.watched >= 1000000:
            value = "%.0f%s" % (i.watched/1000000.00, 'M')
        else:
            if i.watched >= 1000:
                value = "%.0f%s" % (i.watched/1000.0, 'M')
    subscribers = ''
    notifications = ''

    comments = something.objects.filter(comment_video__in=videos).all()
    
    if request.user.is_authenticated:
        subscribers = Channel.objects.filter(subscribers=request.user).all()
        notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')
    form = ChannelCreateForm()
    if request.method == 'POST':
        form = ChannelCreateForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            form.save()
            return redirect('channel', request.user.channeluser.id)
    
    some = something.objects.all()
    print(some)
    context = {
        'value': value,
        'subscribers': subscribers,
        'videos': videos,
        'form': form,
        'notifications': notifications,
        'comments': comments,
    }
    return render(request, 'home.html', context)





def get_videos(request):
    videos = Video.objects.all().order_by("?")
    return JsonResponse(data=list(videos.values()), safe=False)












def explore(request):
    subscribers = ''
    notifications = ''
    videos = Video.objects.all().order_by('-watched')[:100]
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')
        subscribers = Channel.objects.filter(subscribers=request.user).all()

    context = {
        'videos': videos,
        'subscribers': subscribers,
        'notifications': notifications,
    }
    return render(request, 'explore.html', context)


def subscriptions(request):
    ids=[]
    sub = ''
    subscribers = ''
    notifications = ''
    if request.user.is_authenticated:
        sub = Channel.objects.filter(subscribers=request.user).all()
        subscribers = Channel.objects.filter(subscribers=request.user).all()
        notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')
    for i in sub:
        ids.append(i.channeluser)
        
    preserved = Case(*[When(id=id, then=pos) for pos, id in enumerate(ids)])
    vids = Video.objects.filter(author__in=ids).order_by(preserved)
    context = {
        'vids': vids,
        'subscribers': subscribers,
        'notifications': notifications,
    }
    return render(request, 'subscriptions.html', context)


def library(request):
    users = ''
    liked_videos = ''
    subscribers = ''
    notifications = ''
    watchlatervideos = ''
    playlists = ''
    if request.user.is_authenticated:
        playlists = Playlist.objects.filter(playlist_user=request.user).all()
        profile = get_object_or_404(Channel, channeluser=request.user)
        users = profile.history.all()
        liked_videos = Video.objects.filter(liked=request.user).all()
        subscribers = Channel.objects.filter(subscribers=request.user).all()
        notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')
        watchlatervideos = Video.objects.filter(watchlater=request.user).all()

    context = {
        'users': users,
        'liked_videos': liked_videos,
        'subscribers': subscribers,
        'notifications': notifications,
        'watchlatervideos': watchlatervideos,
        'playlists': playlists,
    }
    return render(request, 'library.html', context)


def history(request):
    users = ''
    subscribers = ''
    notifications = ''
    if request.user.is_authenticated:
        profile = get_object_or_404(Channel, channeluser=request.user)
        users = profile.history.all()
        subscribers = Channel.objects.filter(subscribers=request.user).all()
        notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')

    context = {
        'users': users,
        'subscribers': subscribers,
        'notifications': notifications,
    }
    return render(request, 'history.html', context)


def watch(request, id):
    video = get_object_or_404(Video, id=id)
    videos = Video.objects.all().exclude(id=video.id).order_by('?')[:11]
    commentform = ''
    jsoncom = []
    notifications = ''
    comments = something.objects.filter(comment_video=video).all().order_by('-commented_on')
    if comments:
        jsoncom = serializers.serialize('json', comments, ensure_ascii=False)
        
    if request.user.is_authenticated:
        video.watched += 1
        video.save()
        notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')
        profile = get_object_or_404(Channel, channeluser=request.user.channeluser.channeluser)
        if video not in profile.history.all():
            profile.history.add(video)
        if request.user not in video.views.all():
            video.views.add(request.user)

    if request.user.is_authenticated:
        commentform = CommentForm()
        if request.method == 'POST':
            commentform = CommentForm(request.POST or None)
            if commentform.is_valid():
                commentform.save()
                return redirect('watch', video.id)

    context = {
        'video': video,
        'videos': videos,
        'comments': comments,
        'commentform': commentform,
        'notifications': notifications,
        'jsoncom': jsoncom,
    }
    return render(request, 'watch.html', context)





def likes_count(request, id):
    video = get_object_or_404(Video, id=id)
    count = video.liked.all().count()
    return JsonResponse(data={'likes_count': count})



def get_comments(request, id):
    video = get_object_or_404(Video, id=id)
    comments = something.objects.filter(comment_video=video).all().order_by('-commented_on')
    print(comments)
    data = list(comments.values())
    return JsonResponse(data, safe=False)






class LikeNotification(View):
    def get(self, request, id, *args, **kwargs):
        print("+"+id+"+")
        notification = Notification.objects.get(pk=id)
        print(notification)
        notification.is_seen = True
        notification.save()

        return redirect('watch')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
        else:
            return redirect('login')
    return render(request, 'login.html')


def search(request):
    query = request.GET.get('q')
    videos = Video.objects.filter(Q(title__icontains=query) | Q(description__icontains=query)).all()
    users = Channel.objects.filter(channelname__icontains=query).all()
    print(users)
    vids = ''
    for user in users:
        if user in Channel.objects.filter():
            vids = Video.objects.filter(author=user.channeluser)
    subscribers = Channel.objects.filter(subscribers=request.user).all()
    notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')

    context = {
        'videos': videos, 
        'query': query, 
        'users': users, 
        'vids': vids,
        'subscribers': subscribers, 
        'notifications': notifications
    }
    return render(request, 'search.html', context)

def channel(request, id):
    featured = Video.objects.filter(author=request.user).first()
    user = get_object_or_404(Channel, id=id)
    user_videos = Video.objects.filter(author=request.user).all()
    subscribers = Channel.objects.filter(subscribers=request.user).all()
    notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')

    context = {'user_videos': user_videos, 'featured': featured, 'user': user, 'subscribers': subscribers, 'notifications': notifications}
    return render(request, 'channel/channel_home.html', context)

def channel_videos(request, id):
    featured = Video.objects.filter(author=request.user).first()
    user = get_object_or_404(Channel, id=id)
    user_videos = Video.objects.filter(author=request.user).all()
    subscribers = Channel.objects.filter(subscribers=request.user).all()
    notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')

    context = {'user_videos': user_videos, 'featured': featured, 'user': user, 'subscribers': subscribers, 'notifications': notifications}
    return render(request, 'channel/channel_videos.html', context)

def channel_playlists(request, id):
    playlists = Playlist.objects.filter(playlist_user=request.user).all()
    user = get_object_or_404(Channel, id=id)
    context = {
        'user': user,
        'playlists': playlists
    }
    return render(request, 'channel/channel_playlists.html', context)


def channel_channels(request, id):
    playlists = Playlist.objects.filter(playlist_user=request.user).all()
    user = get_object_or_404(Channel, id=id)
    channels = Channel.objects.filter(subscribers=user.channeluser).all()
    context = {
        'user': user,
        'playlists': playlists,
        'channels': channels,
    }
    return render(request, 'channel/channel_channels.html', context)


def channel_about(request, id):
    user = get_object_or_404(Channel, id=id)
    user_videos = Video.objects.filter(author=request.user).all()
    subscribers = Channel.objects.filter(subscribers=request.user).all()
    notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')
    views = Video.objects.filter(author=request.user).all() 
    count = 0
    for i in views:
        count += i.watched

    context = {
        'count': count,
        'user_videos': user_videos,
        'user': user,
        'subscribers': subscribers,
        'notifications': notifications,
    }
    return render(request, 'channel/channel_about.html', context)






@csrf_exempt
def subscribe(request, channelname):
    subchannel = get_object_or_404(Channel, channelname=channelname)
    if request.user.is_authenticated:
        if request.method == 'PUT':
            if request.user not in subchannel.subscribers.all():
                subchannel.subscribers.add(request.user)
                notify = Notification.objects.create(notification_type=2, from_user=request.user, to_user=subchannel.channeluser)
                notify.save()
                return HttpResponseRedirect('')

@csrf_exempt
def unsubscribe(request, channelname):
    subchannel = get_object_or_404(Channel, channelname=channelname)
    if request.user.is_authenticated:
        if request.method == 'PUT':
            if request.user in subchannel.subscribers.all():
                subchannel.subscribers.remove(request.user)
                return HttpResponseRedirect('')


@csrf_exempt
def watchsubscribe(request, id, channelname):
    video = get_object_or_404(Video, id=id)
    subchannel = get_object_or_404(Channel, channelname=channelname)
    if request.user.is_authenticated:
        if request.method == 'POST':
            if request.user not in subchannel.subscribers.all():
                subchannel.subscribers.add(request.user)
                notify = Notification.objects.create(notification_type=2, from_user=request.user, to_user=subchannel.channeluser)
                notify.save()
                return HttpResponseRedirect('')

@csrf_exempt
def watchunsubscribe(request, id, channelname):
    video = get_object_or_404(Video, id=id)
    subchannel = get_object_or_404(Channel, channelname=channelname)
    if request.user.is_authenticated:
        if request.method == 'POST':
            if request.user in subchannel.subscribers.all():
                subchannel.subscribers.remove(request.user)
                return HttpResponseRedirect('')
        




def author_channel(request, channelname):
    channel = get_object_or_404(Channel, channelname=channelname)
    author_videos = Video.objects.filter(author=channel.channeluser).all()
    featured = Video.objects.filter(author=channel.channeluser).first()
    subscribers = Channel.objects.filter(subscribers=request.user).all()
    notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')

    context = {
        'channel': channel,
        'author_videos': author_videos,
        'featured': featured,
        'subscribers': subscribers,
        'notifications': notifications,
    }
    return render(request, 'authorchannel/author_channel_home.html', context)


def author_channel_playlists(request, channelname):
    channel = get_object_or_404(Channel, channelname=channelname)
    playlists = Playlist.objects.filter(playlist_user=channel.channeluser).all()

    context = {
        'playlists': playlists,
        'channel': channel,
    }
    return render(request, 'authorchannel/author_channel_playlists.html', context)


def author_channel_channels(request, channelname):
    channel = get_object_or_404(Channel, channelname=channelname)
    playlists = Playlist.objects.filter(playlist_user=channel.channeluser).all()
    channels = Channel.objects.filter(subscribers=channel.channeluser).all()
    context = {
        'playlists': playlists,
        'channel': channel,
        'channels': channels,
    }
    return render(request, 'authorchannel/author_channel_channels.html', context)



def author_channel_videos(request, channelname):
    channel = get_object_or_404(Channel, channelname=channelname)
    author_videos = Video.objects.filter(author=channel.channeluser).all()
    featured = Video.objects.filter(author=channel.channeluser).first()
    subscribers = Channel.objects.filter(subscribers=request.user).all()
    notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')

    context = {
        'channel': channel,
        'author_videos': author_videos,
        'featured': featured,
        'subscribers': subscribers,
        'notifications': notifications,
    }
    return render(request, 'authorchannel/author_channel_videos.html', context)


def author_channel_about(request, channelname):
    channel = get_object_or_404(Channel, channelname=channelname)
    author_videos = Video.objects.filter(author=channel.channeluser).all()
    featured = Video.objects.filter(author=channel.channeluser).first()
    subscribers = Channel.objects.filter(subscribers=request.user).all()
    notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')
    count = 0
    for i in author_videos:
        count += i.watched

    context = {
        'channel': channel,
        'author_videos': author_videos,
        'featured': featured,
        'subscribers': subscribers,
        'notifications': notifications,
        'count': count,
    }
    return render(request, 'authorchannel/author_channel_about.html', context)






@csrf_exempt
def like(request, id):
    user = request.user
    video = get_object_or_404(Video, id=id)
    if request.user.is_authenticated:
        if request.method == 'POST':
            if user not in video.liked.all():
                video.liked.add(user)
                notif = Notification.objects.create(notification_type=1, to_user=video.author, from_user=user, post=video, is_seen=False)
                notif.save()
                return HttpResponseRedirect('')

@csrf_exempt
def unlike(request, id):
    user = request.user
    video = get_object_or_404(Video, id=id)
    if request.user.is_authenticated:
        if request.method == 'POST':
            if user in video.liked.all():
                video.liked.remove(user)
                notif = Notification.objects.filter(notification_type=1, to_user=video.author, from_user=user, post=video)
                notif.delete()
                return HttpResponseRedirect('')



def notifications(request):
    notifications = Notification.objects.filter(to_user=request.user).all()
    context = {
        'notifications': notifications,
    }
    return render(request, 'notifications.html', context)



def liked_videos(request):
    likedvideos = Video.objects.filter(liked=request.user).all()
    viewcount = 0
    for i in likedvideos:
        viewcount += i.watched
    totalvideos = likedvideos.count
    likedfirst = Video.objects.filter(liked=request.user).all()[:1]
    if request.user.is_authenticated:
        subscribers = Channel.objects.filter(subscribers=request.user).all()
    context = {
        'likedvideos': likedvideos,
        'likedfirst': likedfirst,
        'totalvideos': totalvideos,
        'viewcount': viewcount,
        'subscribers': subscribers
    }
    return render(request, 'liked_videos.html', context)


def watchlater_videos(request):
    likedvideos = Video.objects.filter(watchlater=request.user).all()
    viewcount = 0
    for i in likedvideos:
        viewcount += i.watched
    totalvideos = likedvideos.count
    likedfirst = Video.objects.filter(watchlater=request.user).all()[:1]
    if request.user.is_authenticated:
        subscribers = Channel.objects.filter(subscribers=request.user).all()
    context = {
        'likedvideos': likedvideos,
        'likedfirst': likedfirst,
        'totalvideos': totalvideos,
        'viewcount': viewcount,
        'subscribers': subscribers,
    }
    return render(request, 'watchlater_videos.html', context)




@csrf_exempt
def like_comment(request, id, comment_id):
    user = request.user
    comment = get_object_or_404(something, comment_id=comment_id)
    if request.method == 'PUT':
        if request.user not in comment.comment_like.all():
            comment.comment_like.add(user)
            return HttpResponseRedirect('')

@csrf_exempt
def unlike_comment(request, id, comment_id):
    user = request.user
    comment = get_object_or_404(something, comment_id=comment_id)
    if request.method == 'PUT':
        if request.user in comment.comment_like.all():
            comment.comment_like.remove(user)
            return HttpResponseRedirect('')

@csrf_exempt
def delete_comment(request, id, comment_id):
    user = request.user
    video = get_object_or_404(Video, id=id)
    comment = get_object_or_404(something, comment_id=comment_id)
    if request.method == 'PUT':
        comment.delete()
        return HttpResponseRedirect('')