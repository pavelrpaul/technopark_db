from django.conf.urls import patterns, url

from views import Clear, Status
from views import ForumCreate, ForumDetails, ForumListThreads, ForumListPosts, ForumListUsers
from views import PostCreate, PostDetails, PostList, PostRemove, PostRestore, PostUpdate, PostVote
from views import UserCreate, UserDetails, UserFollow, UserUnfollow, \
                  UserListFollowers, UserListFollowing, UserUpdateProfile, UserListPosts
from views import ThreadCreate, ThreadDetails, ThreadSubscribe, ThreadUnsubscribe, \
                  ThreadOpen, ThreadClose, ThreadVote, ThreadList, ThreadUpdate, \
                  ThreadRemove, ThreadRestore, ThreadListPosts
from views import test


urlpatterns = patterns('',
    url(r'^test/$', test),

    #Common
    url(r'^db/api/clear/$', Clear.a()),
    url(r'^db/api/status/$', Status.a()),
    
    #Forum
    url(r'^db/api/forum/create/$', ForumCreate.a()),
    url(r'^db/api/forum/details/$', ForumDetails.a()),
    url(r'^db/api/forum/listPosts/$', ForumListPosts.a()),
    url(r'^db/api/forum/listThreads/$', ForumListThreads.a()),
    url(r'^db/api/forum/listUsers/$', ForumListUsers.a()),

    #Post
    url(r'^db/api/post/create/$', PostCreate.a()),
    url(r'^db/api/post/details/$', PostDetails.a()),
    url(r'^db/api/post/list/$', PostList.a()),
    url(r'^db/api/post/remove/$', PostRemove.a()),
    url(r'^db/api/post/restore/$', PostRestore.a()),
    url(r'^db/api/post/update/$', PostUpdate.a()),
    url(r'^db/api/post/vote/$', PostVote.a()),

    #User
    url(r'^db/api/user/create/$', UserCreate.a()),
    url(r'^db/api/user/details/$', UserDetails.a()),
    url(r'^db/api/user/follow/$', UserFollow.a()),
    url(r'^db/api/user/listFollowers/$', UserListFollowers.a()),
    url(r'^db/api/user/listFollowing/$', UserListFollowing.a()),
    url(r'^db/api/user/listPosts/$', UserListPosts.a()),
    url(r'^db/api/user/unfollow/$', UserUnfollow.a()),
    url(r'^db/api/user/updateProfile/$', UserUpdateProfile.a()),
    
    #Thread
    url(r'^db/api/thread/close/$', ThreadClose.a()),
    url(r'^db/api/thread/create/$', ThreadCreate.a()),
    url(r'^db/api/thread/details/$', ThreadDetails.a()),
    url(r'^db/api/thread/list/$', ThreadList.a()),
    url(r'^db/api/thread/listPosts/$', ThreadListPosts.a()),
    url(r'^db/api/thread/open/$', ThreadOpen.a()),
    url(r'^db/api/thread/remove/$', ThreadRemove.a()),
    url(r'^db/api/thread/restore/$', ThreadRestore.a()),
    url(r'^db/api/thread/subscribe/$', ThreadSubscribe.a()),
    url(r'^db/api/thread/unsubscribe/$', ThreadUnsubscribe.a()),
    url(r'^db/api/thread/update/$', ThreadUpdate.a()),
    url(r'^db/api/thread/vote/$', ThreadVote.a()),
)
