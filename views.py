# -*- coding: utf-8 -*-
# File: views.py
# Author: Kenson Man
# Date: 2017-05-11 11:53
# Desc: The webframe default views.
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, logout as auth_logout, login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db import transaction
from django.http import HttpResponseForbidden, QueryDict
from django.middleware.csrf import get_token as getCSRF
from django.shortcuts import render, redirect, get_object_or_404 as getObj
from django_tables2 import RequestConfig
from django.utils.translation import ugettext_lazy as _, ugettext as gettext
from django.urls import reverse
from .functions import getBool
from .models import *
from .tables import *
import hashlib, logging

CONFIG_KEY='ConfigKey'
logger=logging.getLogger('webframe.views')

def login( req ):
    '''
    Login the session.
    '''
    params=dict()
    params['next']=req.POST.get('next', req.GET.get('next', reverse('index')))
    if req.method=='POST':
        username=req.POST['username']
        password=req.POST['password']
        try:
           u=authenticate(req, username=username, password=password)
        except:
           logger.debug('Failed to login')
           u=None
        if u:
            auth_login(req, u)
            nextUrl=params.get('next', reverse('index'))
            return redirect(nextUrl)
        messages.warning(req, gettext('Invalid username or password'))
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
        params['btns']=getattr(settings, 'USER_BTNS', None)
        params['AUTH_PASSWORD_REQUIRED']=getBool(getattr(settings, 'AUTH_PASSWORD_REQUIRED', False))
        logger.debug('btns: %s'%params['btns'])
        return render(req, getattr(settings, 'TMPL_USER', 'webframe/user.html'), params)
    elif req.method=='DELETE':
        _('User.msg.confirmDelete')
        user.delete()
        return redirect(args.get('next', 'users'))
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

        if hasattr(settings, 'AUTH_DEFAULT_GROUPS'):
            for g in getattr(settings, 'AUTH_DEFAULT_GROUPS', list()):
               gp=Group.objects.filter(name=g)
               if gp.count()==1:
                  gp[0].user_set.add(user)
        return redirect(args.get('next', 'users'))
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
    if user==None: user=req.user.username
    if user!=req.user.username and not req.user.is_superuser:
        if req.user.username!=user: return HttpResponseForbidden('<h1>403-Forbidden</h1>')
    user=getObj(get_user_model(), username=user)
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
    # Declare the preference's owner
    if user==None or user=='None': user=req.user.username
    if user!=req.user.username and not req.user.is_superuser:
        if req.user.username!=user: return HttpResponseForbidden('<h1>403-Forbidden</h1>')
    user=getObj(get_user_model(), username=user)
    params=dict()

    # Get the target preference
    if prefId=='add' or prefId=='new':
        pref=Preference()
        pref.owner=user
        if 'parent' in req.GET: pref.parent=getObj(Preference, id=req.GET['parent'])
    else:
        pref=getObj(Preference, id=prefId)
    
    if req.method=='GET':
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
        params['childs']=PreferenceTable(pref.childs())
        params['currentuser']=user
        return render(req, getattr(settings, 'TMPL_PREFERENCE', 'webframe/preference.html'), params)
    elif req.method=='POST':
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
        pref.name=req.POST['name']
        pref.value=req.POST['value']
        pref.sequence=int(req.POST['sequence'])
        pref.parent=None if req.POST.get('parent') is None else getObj(Preference, id=req.POST['parent'])
        pref.save()
    elif req.method=='DELETE':
        # Delete the method
        _('Preference.msg.confirmDelete')
        pref.delete()
    if pref.parent:
        return redirect('preference', user=user.username, prefId=pref.parent.id)
    else:
        return redirect('preferences', user=user.username)
        
