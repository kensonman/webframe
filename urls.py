from django.conf.urls import url
from django.views.i18n import JavaScriptCatalog
from . import views
from django.conf import settings

urlpatterns=[
   url(r'^login/?$', views.login, name='login'),
   url(r'^logout/?$', views.logout, name='logout'),

   url(r'^users/?$', views.users, name='users'),
   url(r'^users/(?P<user>[^/]*)/?$', views.user, name='user'),
   url(r'^users/(?P<user>[^/]*)/prefs/?$', views.prefs, name='prefs'),
   url(r'^users/(?P<user>[^/]*)/prefs/(?P<prefId>[^/]*)/?$', views.pref, name='pref'),

   url(r'^jsi18n/webframe/$', JavaScriptCatalog.as_view(), {'packages':('webframe',),'domain':'django'}, name='js'),
   url(r'^ajax/users/?$', views.ajaxUsers, name='ajax-users'),
] 
