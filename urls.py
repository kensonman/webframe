# -*- coding: utf-8 -*-
#
from django.conf import settings
from django.urls import path, re_path, include
from django.views.i18n import JavaScriptCatalog
from . import views

app_name='webframe'
urlpatterns=[
   re_path(r'^login/?$', views.Login.as_view(), name='login'),
   re_path(r'^logout/?$', views.logout, name='logout'),
   re_path(r'^resetPassword/?$', views.ResetPasswordView.as_view(), name='resetPassword'),
   re_path(r'^obtainToken/?$', views.RegisterView.as_view(), name='obtainToken'),
   re_path(r'^register/?$', views.WebAuthnRegistration.as_view(), name='webauthn-registration'),
   re_path(r'^authenticate/?$', views.WebAuthnAuthentication.as_view(), name='webauthn-authentication'),

   re_path(r'^users/?$', views.users, name='users'),
   re_path(r'^users/(?P<user>[^/]*)/?$', views.user, name='user'),
   re_path(r'^users/(?P<user>[^/]*)/prefs/?$', views.prefs, name='prefs'),
   re_path(r'^users/(?P<user>[^/]*)/prefs/(?P<prefId>[^/]*)/?$', views.pref, name='pref'),

   re_path(r'^ajax/users/?$', views.ajaxUsers, name='ajax-users'),
   re_path(r'^ajax/pref/(?P<name>[^/]+)/?$', views.ajaxPref, name='ajax-pref'),     #It can be disabled in WF-AJAX_PREF
   re_path(r'^ajax/prefs/(?P<name>[^/]+)/?$', views.ajaxPrefs, name='ajax-prefs'),  #It can be disabled in WF-AJAX_PREFS

   re_path(r'^prefsDoc/?$', views.prefsDoc, name='prefs-doc'),                      #It can be disabled in WF-PREFS_DOC, required vgallery.view_preference
   re_path(r'^href/menuitem/?$', views.help_menuitem, name='help-menuitem'),
   re_path(r'^href/menuitem/create/?$', views.help_create_menuitem, name='help-create-menuitem'),

   re_path(r'headers/?$', views.HeaderView.as_view(), name='headers'),
   re_path(r'whoami/?$', views.WhoAmIView.as_view(), name='whoami'),

   re_path('jsi18n/', JavaScriptCatalog.as_view(domain='django', packages=['webframe',]), name='js'),
] 
