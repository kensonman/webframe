# -*- coding: utf-8 -*-
# File: views.py
# Author: Kenson Man
# Date: 2017-05-11 11:53
# Desc: The webframe default views.
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, logout as auth_logout, login as auth_login, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.db import transaction
from django.http import HttpResponseForbidden, QueryDict, Http404, JsonResponse
from django.middleware.csrf import get_token as getCSRF
from django.shortcuts import render, redirect, get_object_or_404 as getObj
from django.views import View
from django.utils.translation import ugettext_lazy as _, ugettext as gettext
from django.urls import reverse
from django_tables2 import RequestConfig
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from .decorators import is_enabled
from .functions import getBool, isUUID, LogMessage as lm
from .models import *
from .serializers import APIResult, MenuItemSerializer, UserSerializer
from .tables import *
import hashlib, logging

CONFIG_KEY='ConfigKey'
logger=logging.getLogger('webframe.views')

#Make sure the translation
_('django.contrib.auth.backends.ModelBackend')
_('django_auth_ldap.backend.LDAPBackend')
_('nextPage')
_('thisPage:%(page)s')
_('prevPage')

class Login( View ):
   def __loadDefault__(self, req):
      params=dict()
      try:
         params['next']=req.POST.get('next', req.GET.get('next', reverse('index')))
         if params['next']==reverse('webframe:login'):
            raise ValueError #Make sure do not loopback the login page.
         if params['next']==reverse('webframe:logout'):
            raise ValueError #Make sure do not loopback the login page.
      except:
         params['next']=req.POST.get('next', req.GET.get('next', reverse('index')))
      params['socialLogin_facebook']=hasattr(settings, 'SOCIAL_AUTH_FACEBOOK_KEY')
      params['socialLogin_twitter']=hasattr(settings, 'SOCIAL_AUTH_TWITTER_KEY')
      params['socialLogin_github']=hasattr(settings, 'SOCIAL_AUTH_GITHUB_KEY')
      params['socialLogin_google']=hasattr(settings, 'SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
      req.session['next']=params['next']
      logger.debug('Next URL: {0}'.format(params['next']))
      logger.debug('Login templates: %s'%getattr(settings, 'TMPL_LOGIN', 'webframe/login.html'))
      params['backends']=[_(b) for b in settings.AUTHENTICATION_BACKENDS]
      return params

   def get(self, req):
      'Return the login form'
      params=self.__loadDefault__(req)
      return render(req, getattr(settings, 'TMPL_LOGIN', 'webframe/login.html'), params)

   def post(self, req):
      params=self.__loadDefault__(req)
      username=req.POST['username']
      password=req.POST['password']

      User=get_user_model()
      if User.objects.exclude(username=getattr(settings, 'ANONYMOUS_USER_NAME', 'AnonymousUser')).count()<1:
         ## 2017-09-30 10:44, Kenson Man
         ## Let the first login user be the system administrator
         u=User()
         u.username=username
         u.first_name='System'
         u.last_name='Administrator'
         u.is_staff=True
         u.is_superuser=True
         u.set_password(password)
         u.save()
         messages.warning(req, 'Created the first user %s as system administroator'%username)

      try:
         u=authenticate(req, username=username, password=password)
         try:
            if u.profile:
               if not u.profile.alive:
                  raise Error(lm('User[{0}] is expired! {1}~{2}', u.id, u.profile.effDate, u.profile.expDate))
         except User.profile.RelatedObjectDoesNotExist:
            logger.debug(lm('User<{0}> does not have the related profile, ignore the effective checking!', u.username))
      except:
         logger.debug('Failed to login', exc_info=True)
         u=None
      if u:
         auth_login(req, u)
         nextUrl=params.get('next', reverse('index'))
         return redirect(nextUrl)
      if getattr(settings, 'WF_DEFAULT_LOGIN_WARNINGS', True): messages.warning(req, gettext('Invalid username or password'))
      params['username']=username
      return render(req, getattr(settings, 'TMPL_LOGIN', 'webframe/login.html'), params)

def logout(req):
   '''
   Logout the session.
   '''
   auth_logout(req)
   next=req.POST.get('next', req.GET.get('next', '/'))
   return redirect(next)

@login_required
def users(req):
   '''
   Show the users page. It is supported to the default User Model (django.contrib.auth.models.User)
   '''
   # Check permission
   if req.user.is_superuser:
      pass
   elif req.user.has_perm('auth.browse_user'):
      pass
   else:
      return HttpResponseForbidden('<h1>403 - Forbidden</h1>')

   params=dict()
   params['target']=UserTable(get_user_model().objects.all())
   params['btns']=getattr(settings, 'USERS_BTNS', None)
   rc=RequestConfig(req)
   rc.configure(params['target'])
   return render(req, getattr(settings, 'TMPL_USERS', 'webframe/users.html'), params)

@login_required
def ajaxUsers(req):
   q=req.GET.get('q', None)
   if q and len(q)>=3:
      rst=get_user_model().objects.filter(username__icontains=q).order_by('username')
      data=[{'key':u.id, 'value': u.username} for u in rst]
      return JsonResponse(data, safe=False)
   raise Http404()

@transaction.atomic
@login_required
def user(req, user):
   user=get_user_model()() if user=='add' or user=='new' else getObj(get_user_model(), username=user)
   params=dict()
   args=QueryDict(req.body)

   if req.method=='GET':
      # Check permission
      if req.user.is_superuser:
         pass
      elif req.user.username==username:
         pass
      elif req.user.has_perm('auth.browse_user'):
         pass
      else:
         return HttpResponseForbidden('<h1>403-Forbidden</h1>')

      # Generate the result
      params['target']=user
      params['groups']=Group.objects.all()
      params['btns']=getattr(settings, 'USER_BTNS', None)
      params['AUTH_PASSWORD_REQUIRED']=getBool(getattr(settings, 'AUTH_PASSWORD_REQUIRED', True))
      logger.debug('btns: %s'%params['btns'])
      return render(req, getattr(settings, 'TMPL_USER', 'webframe/user.html'), params)
   elif req.method=='DELETE':
      _('User.msg.confirmDelete')
      user.delete()
      return redirect(args.get('next', 'webframe:users'))
   elif req.method=='POST':
      # Check permission
      if req.user.is_superuser:
         pass
      elif req.user==user:
         pass
      elif user.id is None and req.user.has_perm('auth.add_user'):
         pass
      elif user.id is not None and req.user.has_perm('auth.change_user'):
         pass
      else:
         return HttpResponseForbidden('<h1>403 - Forbidden</h1>')

      user.first_name=req.POST.get('first_name', None)
      user.last_name=req.POST.get('last_name', None)
      user.email=req.POST.get('email', None)
      if req.user.is_superuser or req.user.has_perm('auth.add_user') or req.user.has_perm('auth.change_user'):
         user.username=req.POST.get('username', user.username)
         user.is_superuser = req.POST.get('is_superuser', '').upper() in ['TRUE', 'T', 'YES', 'Y', '1']
         user.is_active = req.POST.get('is_active', '').upper() in ['TRUE', 'T', 'YES', 'Y', '1']
         user.is_staff = req.POST.get('is_staff', '').upper() in ['TRUE', 'T', 'YES', 'Y', '1']
      password=req.POST.get('password', None)
      if password:
         user.set_password(password)
      user.save()

      #2017-09-26 17:21, Kenson Man
      #Implement the groups logic
      user.groups.clear()
      for gid in req.POST.getlist('groups'):
         Group.objects.get(id=gid).user_set.add(user)

      if hasattr(settings, 'AUTH_DEFAULT_GROUPS'):
         for g in getattr(settings, 'AUTH_DEFAULT_GROUPS', list()):
            gp=Group.objects.filter(name=g)
            if gp.count()==1:
              gp[0].user_set.add(user)
      return redirect(args.get('next', 'webframe:users'))
   elif req.method=='PUT': #The PUT method is used for user to update their own personal information, webframe/preferences.html
      # Check permission
      if req.user.is_superuser:
         pass
      elif req.user==user:
         pass
      elif user.id is not None and req.user.has_perm('auth.change_user'):
         pass
      else:
         return HttpResponseForbidden('<h1>403 - Forbidden</h1>')

      user.first_name=req.POST.get('first_name', None)
      user.last_name=req.POST.get('last_name', None)
      user.email=req.POST.get('email', None)
      user.save()
      return redirect(args.get('next', 'users'))

@login_required
def prefs(req, user=None):
   '''
   Show the preference page of the specified user. 
   If requesting to show user that is not current session,
   the superuser permission are required.
   '''
   if user=='_': return redirect('webframe:prefs', user=req.user)
   if user==None: user=req.user.username
   if user!=req.user.username and not req.user.is_superuser:
      if req.user.username!=user: return HttpResponseForbidden('<h1>403-Forbidden</h1>')
   user=getObj(get_user_model(), username=user)
   if req.method=='POST':
      newPwd=req.POST.get('newPwd', None)
      if newPwd and newPwd==req.POST.get('rePwd', None):
         user.set_password(newPwd)
         user.save()
         auth_logout(req)
         return redirect('webframe:prefs', user=user)

   params=dict()
   params['preference']=PreferenceTable(Preference.objects.filter(owner=req.user, parent__isnull=True))
   params['config']=PreferenceTable(Preference.objects.filter(owner__isnull=True, parent__isnull=True))
   rc=RequestConfig(req)
   rc.configure(params['preference'])
   rc.configure(params['config'])
   params['currentuser']=user
   if req.user.has_perm('webframe.add_config') or req.user.has_perm('webframe.change.config'):
      m=hashlib.md5()
      m.update(user.username.encode('utf-8'))
      m.update(CONFIG_KEY.encode('utf-8'))
      params['config_key']=m.hexdigest()
   return render(req, getattr(settings, 'TMPL_PREFERENCES', 'webframe/preferences.html'), params)

@transaction.atomic
@login_required
def pref(req, user=None, prefId=None):
   '''
   Showing the preference form for input.
   '''
   if user=='_': return redirect('webframe:pref', user=req.user, prefId=prefId)
   # Declare the preference's owner
   if user:
      if user.upper()=='NONE': 
         user=None
      else:
         if user!=req.user.username and not req.user.is_superuser:
            if req.user.username!=user: return HttpResponseForbidden('<h1>403-Forbidden</h1>')
         user=getObj(get_user_model(), username=user)
   params=dict()
   params['TYPES']=Preference.TYPES

   # Get the target preference
   if prefId=='add' or prefId=='new':
      pref=Preference()
      pref.owner=user
      if 'parent' in req.GET: pref.parent=getObj(Preference, id=req.GET['parent'])
   elif isUUID(prefId):
      pref=getObj(Preference, id=prefId)
   else:
      pref=getObj(Preference, name=prefId, owner=user)
      if 'admin' in req.GET and req.GET['admin'] in  TRUE_VALUES: return redirect('admin:webframe_preference_change', object_id=pref.id)
      return redirect('webframe:pref', prefId=pref.id, user=user.username if user else 'none')
   
   if req.method=='GET':
      if 'admin' in req.GET and req.GET['admin'] in  TRUE_VALUES: return redirect('admin:webframe_preference_change', object_id=pref.id)
      isConfig=getBool(req.GET.get('config', 'False'))
      if isConfig:
         if not (req.user.has_perm('webframe.add_config') or req.user.has_perm('webframe.change_config')):
            # Returns 403 if user cannot edit config
            return HttpResponseForbidden('<h1>403-Forbidden</h1>')
         pref.owner=None
      else:
         pref.owner=user
      # Preparing the form view
      params['target']=pref
      params['childs']=PreferenceTable(pref.childs)
      params['currentuser']=user
      params['TYPES']=Preference.TYPES
      return render(req, getattr(settings, 'TMPL_PREFERENCE', 'webframe/preference.html'), params)
   elif req.method=='POST' or req.method=='PUT':
      # Security Checking
      if req.POST.get('owner', None):
         if pref.isNew() and req.user.has_perm('webframe.add_preference'):
            pass #Allow to add preference
         elif (not pref.isNew()) and req.user.has_perm('webframe.change_preference'):
            pass #Allow to change preference
         else:
            logger.warning('Forbidden to add or change preference')
            return HttpResponseForbidden('<h1>403-Forbidden</h1>')
         pref.owner=getObj(get_user_model(), id=req.POST['owner'])
      else:
         if pref.isNew() and req.user.has_perm('webframe.add_config'):
            pass #Allow to add config 
         elif (not pref.isNew()) and req.user.has_perm('webframe.change_config'):
            pass #Allow to change config 
         else:
            logger.warning('Forbidden to add or change config')
            return HttpResponseForbidden('<h1>403-Forbidden</h1>')
         pref.owner=None

      # Saving
      pref.tipe=int(req.POST['tipe'])
      pref.name=req.POST['name']
      pref.value=req.POST['value']
      pref.sequence=int(req.POST['sequence'])
      pref.parent=None if req.POST.get('parent') is None else getObj(Preference, id=req.POST['parent'])
      pref.save()
   elif req.method=='DELETE':
      # Delete the method
      _('Preference.msg.confirmDelete')
      pref.delete()

   if req.POST.get('nextUrl', None):
      return redirect(req.POST.get('nextUrl', '/'))

   if pref.parent:
      return redirect('webframe:pref', user=pref.parent.owner, prefId=pref.parent.id)
   else:
      logger.warning('saved without parent')
      return redirect('webframe:prefs', user=pref.owner if pref.owner else req.user)
      
@login_required
@is_enabled('WF-AJAX_PREF')
def ajaxPref(req, name):
   '''
   Get the preference according to the name in JSON format
   '''
   logger.debug('Getting pref<{0}>'.format(name))
   rst=Preference.objects.pref(name, user=req.user, defval=None, returnValue=False)
   rst={'name': rst.name, 'value': rst.value, 'id': rst.id}
   return JsonResponse(rst, safe=False)

@login_required
@is_enabled('WF-AJAX_PREFS')
def ajaxPrefs(req, name):
   '''
   Get the preferences according to the name in JSON format
   '''
   logger.debug('Getting prefs<{0}>'.format(name))
   rst=Preference.objects.pref(name, user=req.user, defval=None, returnValue=False)
   rst=[{'id': i.id, 'name':i.name, 'value':i.value} for i in rst.childs]
   return JsonResponse(rst, safe=False)

@login_required
@permission_required('webframe.view_preference')
@is_enabled('WF-PREFS_DOC')
def prefsDoc(req):
   '''
   Show the preference docs
   '''
   logger.debug('Showing the prefs-doc...')
   params=dict()
   params['target']=Preference.objects.filter(parent__isnull=True).order_by('owner', 'sequence', 'name')
   params['TYPES']=Preference.TYPES
   params['now']=getTime('now')
   return render(req, 'webframe/prefsDoc.html', params)

def help_menuitem(req):
   params=dict()
   return render(req, 'webframe/menuitem.html', params)

@login_required
@permission_required('webframe.add_menuitem')
def help_create_menuitem(req):
   if req.method=='POST':
      root=MenuItem(name='/', label=_('appName'))
      root.save()
      lm=MenuItem(name='/Left', parent=root)
      lm.save()
      lroot=MenuItem(name='/Left/Root', label='Goto Root', parent=lm)
      lroot.save()
      rm=MenuItem(name='/Right', parent=root, props={'class': 'navbar-right'})
      rm.save()
      hi=MenuItem(name='/Right/Hi', parent=rm, label='Hi, {{username}}')
      hi.save()
      logout=MenuItem(name='/Right/Hi/Logout', parent=hi, label='Logout', props={'href': reverse('webframe:logout')})
      logout.save()
      return redirect('admin:webframe_menuitem_changelist')
   return HttpResponseForbidden()

class WhoAmIView(APIView):
   authentication_classes = [authentication.TokenAuthentication, authentication.SessionAuthentication]
   permission_classes = [permissions.IsAuthenticatedOrReadOnly]
   
   def get(self, req, format=None):
      return Response(UserSerializer(req.user).data)

class HeaderView(APIView):
   authentication_classes = [authentication.TokenAuthentication, authentication.SessionAuthentication]
   permission_classes = [permissions.IsAuthenticatedOrReadOnly]
      
   def get(self, req, format=None):
      logger.warn(req.method)
      qs=MenuItem.objects.filter(parent__isnull=True)
      if req.user.is_authenticated:
         qs=qs.filter(models.Q(user__isnull=True)|models.Q(user=req.user)).order_by('-user')
      else:
         qs=qs.filter(user__isnull=True).order_by('-user')
      qs=MenuItem.filter(qs, req.user)
      if len(qs)>0:
         return Response(MenuItemSerializer(qs[0]).data)
      else:
         rst=MenuItem(name='Generated NavBar', label=_('appName'))
         lhs=MenuItem(parent=rst)
         hlp=MenuItem(parent=lhs, label='MenuItem Help', props={'href': reverse('webframe:help-menuitem')})
         lhs.childs=[hlp,]
         rst.childs=[lhs,]
         return Response(MenuItemSerializer(rst).data)
