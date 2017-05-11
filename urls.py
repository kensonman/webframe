from django.conf.urls import url
from . import views
from django.conf import settings

urlpatterns=[
	url(r'^login/$', views.login, name='login'),
	url(r'^logout/$', views.logout, name='logout'),
	url(r'^users/$', views.users, name='users'),
	url(r'^users/(?P<username>[^/]*)/$', views.user, name='user'),
] 
