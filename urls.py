from django.conf.urls import url
from . import views
from django.conf import settings

urlpatterns=[
	url(r'^login/?$', views.login, name='login'),
	url(r'^logout/?$', views.logout, name='logout'),
	url(r'^users/?$', views.users, name='users'),
	url(r'^users/(?P<user>[^/]*)/?$', views.user, name='user'),
	url(r'^users/(?P<user>[^/]*)/prefs/?$', views.prefs, name='prefs'),
	url(r'^users/(?P<user>[^/]*)/prefs/(?P<prefId>[^/]*)/?$', views.pref, name='pref'),
] 