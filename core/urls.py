from django.conf.urls import url

from core import info, user

urlpatterns = [
    url(r'^$', info.index, name='index'),
    url(r'clear', info.clear, name='clear'),
    url(r'status', info.status, name='status'),
    url(r'user/create', user.create, name='user_create'),
]