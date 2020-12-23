# -*- coding: utf-8 -*-
#
from django.conf import settings
from django.urls import path, re_path, include
from django.views.i18n import JavaScriptCatalog
from . import views

app_name='webframe'
urlpatterns=[
   re_path(r'^login/?$', views.login, name='login'),
   re_path(r'^logout/?$', views.logout, name='logout'),

   re_path(r'^users/?$', views.users, name='users'),
   re_path(r'^users/(?P<user>[^/]*)/?$', views.user, name='user'),
   re_path(r'^users/(?P<user>[^/]*)/prefs/?$', views.prefs, name='prefs'),
   re_path(r'^users/(?P<user>[^/]*)/prefs/(?P<prefId>[^/]*)/?$', views.pref, name='pref'),

   re_path(r'^ajax/users/?$', views.ajaxUsers, name='ajax-users'),
   re_path(r'^ajax/pref/(?P<name>[^/]+)/?$', views.ajaxPref, name='ajax-pref'),     #It can be disabled in WF-AJAX_PREF
   re_path(r'^ajax/prefs/(?P<name>[^/]+)/?$', views.ajaxPrefs, name='ajax-prefs'),  #It can be disabled in WF-AJAX_PREFS

   re_path(r'^prefsDoc/?$', views.prefsDoc, name='prefs-doc'),                      #It can be disabled in WF-PREFS_DOC, required vgallery.view_preference

   re_path('jsi18n/', JavaScriptCatalog.as_view(domain='django', packages=['webframe',]), name='js'),
] 
