from django.urls import path
from .views import shorts, author_channel_videos, channel, channel_videos, channel_about,explore, home, library, like, login, notifications, search, subscribe, subscriptions, unlike, unsubscribe, watch, author_channel, history, LikeNotification, liked_videos, watchlater_videos, author_channel_about, watchsubscribe, watchunsubscribe, channel_playlists, author_channel_playlists, channel_channels, author_channel_channels, like_comment, unlike_comment, APIView, VideoView, UserView, delete_comment, get_comments, get_videos, ReactView, load_articles, nointernet

urlpatterns = [
    path('', home, name=''),
    path('feed/shorts/<int:id>', shorts, name='shorts'),
    path('get_videos', get_videos, name='get_videos'),
    path('api', ReactView.as_view(), name='api'),
    path('userapi', UserView.as_view(), name='userapi'),
    path('api/<str:id>', VideoView.as_view(), name='videoview'),
    path('login', login, name='login'),
    path('watch/<str:id>', watch, name='watch'),

    path('watch/<str:id>/comments', get_comments, name='get_comments'),

    path('watch/<str:id>/<str:comment_id>/like', like_comment, name='like_comment'),
    path('watch/<str:id>/<str:comment_id>/unlike', unlike_comment, name='unlike_comment'),

    path('watch/<str:id>/<str:comment_id>/delete', delete_comment, name='delete_comment'),

    path('feed/explore', explore, name='explore'),
    path('feed/history', history, name='history'),
    path('feed/library', library, name='library'),
    path('feed/subscriptions', subscriptions, name='subscriptions'),
    path('search', search, name='search'),
    path('notifications', notifications, name='notifications'),

    path('playlist', liked_videos, name='liked_videos'),
    path('wplaylist', watchlater_videos, name='watchlater_videos'),

    path('watch/<str:id>/like', like, name='like'),
    path('watch/<str:id>/unlike', unlike, name='unlike'),
    path('watch/<str:id>/<str:channelname>/subscribe', watchsubscribe, name='watchsubscribe'),
    path('watch/<str:id>/<str:channelname>/unsubscribe', watchunsubscribe, name='watchunsubscribe'),


    path('channel/<str:id>', channel, name='channel'),
    path('channel/<str:id>/videos', channel_videos, name='channel_videos'),
    path('channel/<str:id>/playlists', channel_playlists, name='channel_playlists'),
    path('channel/<str:id>/about', channel_about, name='channel_about'),
    path('channel/<str:id>/channels', channel_channels, name='channel_channels'),



    path('c/<str:channelslug>', author_channel, name='author_channel'),
    path('c/<str:channelslug>/videos', author_channel_videos, name='author_channel_videos'),
    path('c/<str:channelslug>/about', author_channel_about, name='author_channel_about'),
    path('c/<str:channelslug>/playlists', author_channel_playlists, name='author_channel_playlists'),
    path('c/<str:channelslug>/channels', author_channel_channels, name='author_channel_channels'),


    path('c/<str:channelslug>/subscribe', subscribe, name='subscribe'),
    path('c/<str:channelslug>/unsubscribe', unsubscribe, name='unsubscribe'),


    path('load_articles/', load_articles, name='load_articles'),
    path('offline/', nointernet, name='nointernet'),

]
