from datetime import date
from multiprocessing import context
from urllib import response
from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from .forms import ChannelCreateForm, CommentForm
from .models import Channel, Notification, Video, Comment, something, Playlist, HistoryVideo, Shorts
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
from django.core import serializers
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage
from django.template import engines
from django.utils.timezone import now

def format_views_as_K(value):
    if value >= 10 ** 9:  # 1 Billion and above
        return f'{value / 10 ** 9:.1f}B'
    elif value >= 10 ** 6:  # 1 Million and above
        return f'{value / 10 ** 6:.1f}M'
    elif value >= 10 ** 3:  # 1 Thousand and above
        return f'{value / 10 ** 3:.1f}K'
    else:
        return str(value)
def time_ago(value):
    if not value:
        return ""

    now_utc = now()
    time_difference = now_utc - value

    if time_difference.days > 365:
        return f'{time_difference.days // 365} years ago'
    elif time_difference.days > 30:
        return f'{time_difference.days // 30} months ago'
    elif time_difference.days > 7:
        return f'{time_difference.days // 7} weeks ago'
    elif time_difference.days > 1:
        return f'{time_difference.days} days ago'
    elif time_difference.seconds > 3600:
        return f'{time_difference.seconds // 3600} hours ago'
    elif time_difference.seconds > 60:
        return f'{time_difference.seconds // 60} minutes ago'
    else:
        return f'{time_difference.seconds} seconds ago'
# def get_videos(request):
#     engine = engines['django']
#     page = request.GET.get('page')
#     if page is None or not page.isdigit() or int(page) < 1:
#         page = 1
#     videos = Video.objects.all().order_by('-views')
#     paginator = Paginator(videos, 6)

#     try:
#         videos_page = paginator.page(page)
#     except EmptyPage:
#         return JsonResponse({'error': 'No more posts available'})
    
#     serialized_videos = [
#         {
#             'id': video.id,
#             'visibility': video.visibility,
#             'title': video.title, 
#             'author': video.author.channeluser.channelname,
#             'author_image': video.author.channeluser.channelimg.url,
#             'authorchannelurl': 'c/'+video.author.channeluser.channelslug,
#             'image': video.image.url,
#             'video': video.video.url,
#             'duration': video.duration,
#             'description': video.description,
#             'published': time_ago(video.published),
#             'views': format_views_as_K(video.views),
#             'liked': video.liked.count(),
#             'watchlater': video.watchlater.count(),
#             'currentuser': request.user.channeluser.channelname,
#             'currentuserchannelurl': 'channel/'+request.user.channeluser.id,
#             }
#         for video in videos_page
#     ]

#     return JsonResponse({'videos': serialized_videos})




def video_title_suggestions(request):
    user_input = request.GET.get('input', '').strip()
    suggestions = []

    if user_input:
        videos = Video.objects.filter(title__icontains=user_input)[:10]
        suggestions = [{'id': video.id, 'title': video.title} for video in videos]

    return JsonResponse({'suggestions': suggestions})



def load_articles(request):
    articles = Video.objects.all()
    
    data = [{'id': article.id, 'visibility': article.visibility, 'title': article.title, 'author': article.author.username, 'image': article.image.url, 'video': article.video.url, 'duration': article.duration, 'description': article.description, 'published': article.published, 'views': article.views} for article in articles]
    
    return JsonResponse({'videos': data})

def format_video_views(views):
    return "{:,}".format(views)

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
    subscribers = ''
    notifications = ''

    articles = Video.objects.all()
    serialized_events = serializers.serialize('json', articles)

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
    context = {
        'subscribers': subscribers,
        'videos': videos,
        'form': form,
        'notifications': notifications,
        'comments': comments,
    }
    return render(request, 'home.html', context)


def shorts(request, id):
    shorts = get_object_or_404(Shorts, pk=id)
    return render(request, 'shorts.html', {'shorts': shorts})









def explore(request):
    subscribers = ''
    notifications = ''
    videos = Video.objects.all().order_by('-views')[:100]
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
    subscribers = ''
    notifications = ''
    # if request.user.is_authenticated:
    #     sub = Channel.objects.filter(subscribers=request.user).all()
    #     subscribers = Channel.objects.filter(subscribers=request.user).all()
    #     notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')
    # for i in sub:
    #     ids.append(i.channeluser)

    # preserved = Case(*[When(id=id, then=pos) for pos, id in enumerate(ids)])
    # vids = Video.objects.filter(author__in=ids).order_by(preserved)

    if request.user.is_authenticated:
        sub_channels = Channel.objects.filter(subscribers=request.user)
        sub_videos = Video.objects.filter(author__channeluser__in=sub_channels).all()


    context = {
        'vids': sub_videos,
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
        users = HistoryVideo.objects.filter(his_user=request.user).all().order_by('-his_time')
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
    hisvideos = ''
    if request.user.is_authenticated:
        profile = get_object_or_404(Channel, channeluser=request.user)
        users = profile.history.all()
        hisvideos = HistoryVideo.objects.filter(his_user=request.user).all().order_by('-his_time')
        subscribers = Channel.objects.filter(subscribers=request.user).all()
        notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')

    context = {
        'users': users,
        'subscribers': subscribers,
        'notifications': notifications,
        'hisvideos': hisvideos,
    }
    return render(request, 'history.html', context)

import random

def watch(request, id):
    video = get_object_or_404(Video, id=id)
    # title_videos = Video.objects.filter(title__icontains=video.title).exclude(id=video.id).all()
    # author_videos = Video.objects.filter(author=video.author).exclude(id=video.id).all()
    # description_videos = Video.objects.filter(description__icontains=video.description).exclude(id=video.id).all()

    somes = Video.objects.exclude(id=video.id).all().order_by("?")

    # videos = list(author_videos) + list(title_videos) + list(description_videos)
    videos = somes
    # random.shuffle(videos)
    
    history_video = HistoryVideo.objects.filter(his_user=request.user, his_video=video).first()
    if history_video:
        history_video.his_time = timezone.now()
        history_video.save()
    else:
        HistoryVideo.objects.create(his_user=request.user, his_video=video, his_time=timezone.now())

    notif_id = request.POST.get('v')
    if notif_id:
        notif_id = request.POST.get('v')   
        notifs = Notification.objects.filter(post=video, id=notif_id).first()
        if notifs:
            notifs.is_seen = True
            notifs.save()

    commentform = ''
    jsoncom = []
    notifications = ''
    comments = something.objects.filter(
        comment_video=video).all().order_by('-commented_on')
    if comments:
        jsoncom = serializers.serialize('json', comments, ensure_ascii=False)

    if request.user.is_authenticated:
        video.views += 1
        video.save()
        notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')
        profile = get_object_or_404(
            Channel, channeluser=request.user.channeluser.channeluser)
        if video not in profile.history.all():
            profile.history.add(video)

    if request.user.is_authenticated:
        commentform = CommentForm()
        if request.method == 'POST':
            commentform = CommentForm(request.POST or None)
            if commentform.is_valid():
                commentform.save()
                # if request.user != video.author:
                #     notify = Notification.objects.create(notification_type=3, from_user=request.user, to_user=video.author, post=video)
                #     notify.save()
                return redirect('watch', video.id)

    context = {
        'id': id,
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
    comments = something.objects.filter(
        comment_video=video).all().order_by('-commented_on')
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
    videos = Video.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)).all()
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
    featured = Video.objects.filter(author=request.user).order_by('-views').first()
    user = get_object_or_404(Channel, id=id)
    user_videos = Video.objects.filter(author=request.user).all()
    subscribers = Channel.objects.filter(subscribers=request.user).all()
    notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')

    context = {'user_videos': user_videos, 'featured': featured, 'user': user,
               'subscribers': subscribers, 'notifications': notifications}
    return render(request, 'channel/channel_home.html', context)


def channel_videos(request, id):
    featured = Video.objects.filter(author=request.user).first()
    user = get_object_or_404(Channel, id=id)
    user_videos = Video.objects.filter(author=request.user).all()
    subscribers = Channel.objects.filter(subscribers=request.user).all()
    notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')

    context = {'user_videos': user_videos, 'featured': featured, 'user': user,
               'subscribers': subscribers, 'notifications': notifications}
    return render(request, 'channel/channel_videos.html', context)


def channel_playlists(request, id):
    playlists = Playlist.objects.filter(playlist_user=request.user).all()
    notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')
    subscribers = Channel.objects.filter(subscribers=request.user).all()
    user = get_object_or_404(Channel, id=id)
    context = {
        'user': user,
        'playlists': playlists,
        'notifications': notifications,
        'subscribers': subscribers,
    }
    return render(request, 'channel/channel_playlists.html', context)


def channel_channels(request, id):
    playlists = Playlist.objects.filter(playlist_user=request.user).all()
    user = get_object_or_404(Channel, id=id)
    channels = Channel.objects.filter(subscribers=user.channeluser).all()
    notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')
    subscribers = Channel.objects.filter(subscribers=request.user).all()
    context = {
        'user': user,
        'playlists': playlists,
        'channels': channels,
        'notifications': notifications,
        'subscribers': subscribers,
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
        count += i.views

    context = {
        'count': count,
        'user_videos': user_videos,
        'user': user,
        'subscribers': subscribers,
        'notifications': notifications,
    }
    return render(request, 'channel/channel_about.html', context)


@csrf_exempt
def subscribe(request, channelslug):
    subchannel = get_object_or_404(Channel, channelslug=channelslug)
    if request.user.is_authenticated:
        if request.method == 'PUT':
            if request.user not in subchannel.subscribers.all():
                subchannel.subscribers.add(request.user)
                notify = Notification.objects.create(
                    notification_type=2, from_user=request.user, to_user=subchannel.channeluser)
                notify.save()
                return HttpResponseRedirect('', channelslug)


@csrf_exempt
def unsubscribe(request, channelslug):
    subchannel = get_object_or_404(Channel, channelslug=channelslug)
    if request.user.is_authenticated:
        if request.method == 'PUT':
            if request.user in subchannel.subscribers.all():
                subchannel.subscribers.remove(request.user)
                return HttpResponseRedirect('', channelslug)


@csrf_exempt
def watchsubscribe(request, id, channelname):
    video = get_object_or_404(Video, id=id)
    subchannel = get_object_or_404(Channel, channelname=channelname)
    if request.user.is_authenticated:
        if request.method == 'POST':
            if request.user not in subchannel.subscribers.all():
                subchannel.subscribers.add(request.user)
                notify = Notification.objects.create(
                    notification_type=2, from_user=request.user, to_user=subchannel.channeluser)
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


def author_channel(request, channelslug):
    channel = get_object_or_404(Channel, channelslug=channelslug)
    author_videos = Video.objects.filter(author=channel.channeluser).all()
    featured = Video.objects.filter(author=channel.channeluser).first()
    subscribers = Channel.objects.filter(subscribers=request.user).all()
    notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')
    
    print(channel.channeluser)

    notif_id = request.POST.get('v')
    if notif_id:
        notif_id = request.POST.get('v')   
        notifs = Notification.objects.filter(from_user=channel.channeluser, id=notif_id).first()
        print(notifs.from_user)
        print(notifs)
        notifs.is_seen = True
        notifs.save()
    # notif = Notification.objects.get(to_user=request.user, is_seen=False).update(is_seen=True)
    # notif = Notification.objects.filter(to_user=request.user, notification_type=2).first()
    # print(notif)

    context = {
        'channel': channel,
        'author_videos': author_videos,
        'featured': featured,
        'subscribers': subscribers,
        'notifications': notifications,
    }
    return render(request, 'authorchannel/author_channel_home.html', context)


def author_channel_playlists(request, channelslug):
    channel = get_object_or_404(Channel, channelslug=channelslug)
    playlists = Playlist.objects.filter(
        playlist_user=channel.channeluser).all()

    context = {
        'playlists': playlists,
        'channel': channel,
    }
    return render(request, 'authorchannel/author_channel_playlists.html', context)


def author_channel_channels(request, channelslug):
    channel = get_object_or_404(Channel, channelslug=channelslug)
    playlists = Playlist.objects.filter(
        playlist_user=channel.channeluser).all()
    channels = Channel.objects.filter(subscribers=channel.channeluser).all()
    context = {
        'playlists': playlists,
        'channel': channel,
        'channels': channels,
    }
    return render(request, 'authorchannel/author_channel_channels.html', context)


def author_channel_videos(request, channelslug):
    channel = get_object_or_404(Channel, channelslug=channelslug)
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


def author_channel_about(request, channelslug):
    channel = get_object_or_404(Channel, channelslug=channelslug)
    author_videos = Video.objects.filter(author=channel.channeluser).all()
    featured = Video.objects.filter(author=channel.channeluser).first()
    subscribers = Channel.objects.filter(subscribers=request.user).all()
    notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')
    count = 0
    for i in author_videos:
        count += i.views

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
        if request.method == 'PUT':
            if user not in video.liked.all():
                video.liked.add(user)
                if request.user != video.author:
                    notif = Notification.objects.create(notification_type=1, to_user=video.author, from_user=user, post=video, is_seen=False)
                    notif.save()
                return HttpResponseRedirect('')


@csrf_exempt
def unlike(request, id):
    user = request.user
    video = get_object_or_404(Video, id=id)
    if request.user.is_authenticated:
        if request.method == 'PUT':
            if user in video.liked.all():
                video.liked.remove(user)
                if request.user != video.author:
                    notif = Notification.objects.filter(notification_type=1, to_user=video.author, from_user=user, post=video)
                    notif.delete()
                return HttpResponseRedirect('')


def notifications(request):
    notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all()
    context = {
        'notifications': notifications,
    }
    return render(request, 'notifications.html', context)


def liked_videos(request):
    likedvideos = Video.objects.filter(liked=request.user).all()
    viewcount = 0
    for i in likedvideos:
        viewcount += i.views
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
        viewcount += i.views
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



def nointernet(request):
    return render(request, 'nointernet.html')