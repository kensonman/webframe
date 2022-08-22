# -*- coding: utf-8 -*-
# File: views.py
# Author: Kenson Man
# Date: 2017-05-11 11:53
# Desc: The webframe default views.
from base64 import b64encode as b64enc, b64decode as b64dec
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, logout as auth_logout, login as auth_login, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseForbidden, QueryDict, Http404, HttpResponse, JsonResponse
from django.middleware.csrf import get_token as getCSRF
from django.shortcuts import render, redirect, get_object_or_404 as getObj
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _, ugettext as gettext, activate
from django.urls import reverse
from django_tables2 import RequestConfig
from rest_framework import authentication, permissions
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from .tasks import sendEmail
from .decorators import is_enabled
from .functions import getBool, isUUID, LogMessage as lm, getClientIP, getTime
from .models import *
from .serializers import APIResult, MenuItemSerializer, UserSerializer
from .tables import *
import hashlib, logging, json, sys

CONFIG_KEY='ConfigKey'
SESSION_WEBAUTHN_CHALLENGE='webauthn-challenge'
logger=logging.getLogger('webframe.views')

#Make sure the translation
_('django.contrib.auth.backends.ModelBackend')
_('django_auth_ldap.backend.LDAPBackend')
_('nextPage')
_('thisPage:%(page)s')
_('prevPage')

def getAbsoluteUrl(req):
   url=getattr(settings, 'ABSOLUTE_PATH', req.build_absolute_uri('/')[:-1])
   try:
      if not url:
         host=req.build_absolute_uri()
         host=host[0:host.index('/', 9)]
         url=host
      elif url.index('%s')>=0:
         host=req.build_absolute_uri()
         host=host[0:host.index('/', 9)]
         url=url%host
   except ValueError:
      ''' url.index('%s') will raise the ValueError if string not found '''
      pass
   return url

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
      params['allow_registration']=getattr(settings, 'WEBAUTHN_ALLOW_REGISTRATION', False)
      return render(req, getattr(settings, 'TMPL_LOGIN', 'webframe/login.html'), params)

   def login(self, req, username, password):
      params=self.__loadDefault__(req)

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
         if not u: raise AttributeError
         if not hasattr(u, 'profile'): raise TypeError
         if u.profile:
            if not u.profile.alive:
               raise Error(lm('User[{0}] is expired! {1}~{2}', u.id, u.profile.effDate, u.profile.expDate))
      except AttributeError:
         logger.debug(lm('User<{0}> cannot be found, or the password is incorrect.', username))
      except (User.profile.RelatedObjectDoesNotExist, TypeError):
         logger.debug(lm('User<{0}> does not have the related profile, ignore the effective checking!', username))
      except:
         logger.debug('Failed to login', exc_info=True)
         u=None
      return u

   def post(self, req):
      params=self.__loadDefault__(req)
      username=req.POST['username']
      password=req.POST['current-password']
      u=self.login(req, username, password)
      if u:
         auth_login(req, u)
         nextUrl=params.get('next', reverse('index'))
         return redirect(nextUrl)
      if getattr(settings, 'WF_DEFAULT_LOGIN_WARNINGS', True): messages.warning(req, gettext('Invalid username or password'))
      params['username']=username
      return render(req, getattr(settings, 'TMPL_LOGIN', 'webframe/login.html'), params)
      
   def delete(self, req):
      auth_logout(req)
      next=req.POST.get('next', req.GET.get('next', '/'))
      return redirect(next)

class WebAuthnRegistration( View ):
   def get(self, req):
      params=dict()
      if req.headers.get('Accept')=='application/json':
         from webauthn import generate_registration_options, options_to_json
         from webauthn.helpers.structs import AuthenticatorSelectionCriteria, AuthenticatorAttachment, ResidentKeyRequirement
         username=req.GET.get('username')
         displayName=req.GET.get('displayName', username)
         authenticator=req.GET.get('authenticator', '')
         if authenticator and authenticator=='cross-platform':
            authenticator=AuthenticatorSelectionCriteria(authenticator_attachment=AuthenticatorAttachment.CROSS_PLATFORM, resident_key=ResidentKeyRequirement.REQUIRED)
         else:
            authenticator=AuthenticatorSelectionCriteria(authenticator_attachment=AuthenticatorAttachment.PLATFORM, resident_key=ResidentKeyRequirement.REQUIRED)
         opts=generate_registration_options(
              rp_id=getattr(settings, 'WEBAUTHN_RP_ID', 'webframe.kenson.idv.hk')
            , rp_name=getattr(settings, 'WEBAUTHN_RP_NAME', 'webframe')
            , user_id=username
            , user_display_name=displayName
            , user_name=username
            , authenticator_selection=authenticator
            )
         req.session[SESSION_WEBAUTHN_CHALLENGE]=b64enc(opts.challenge).decode('utf-8') #Due to opts.challenge is bytes array which is not serializable
         u=get_user_model().objects.filter(username=username)
         rst=options_to_json(opts)
         rst=json.loads(rst)
         rst['newUserExists']=len(u)>0 and req.user.username!=username
         rst['passwordAvailable']=getattr(req.user, 'password', None)!=None
         rep=HttpResponse()
         rep.headers['Content-Type']='application/json'
         rep.write(json.dumps(rst))
         return rep
      if getattr(settings, 'WEBAUTHN_ALLOW_REGISTRATION', False):
         return render(req, getattr(settings, 'TMPL_WEBAUTHN_REGISTRATION', 'webframe/webauthn-registration.html'), params)
      logger.warning('The configuration is not accept the registration. Use "WEBAUTHN_ALLOW_REGISTRATION=True" in settings.py to turn on')
      rep=HttpResponse(status=406)
      rep.write('SERVER IS NOT ACCEPT REGISTRATION')
      return rep

   @transaction.atomic
   def post(self, req):
      from webauthn import verify_registration_response, base64url_to_bytes, options_to_json
      from webauthn.helpers.structs import RegistrationCredential
      rep=HttpResponse()
      rep.headers['Content-Type']='application/json'
      result=dict()
      try:
         data=req.body.decode('utf-8')
         logger.info(data)
         cred=RegistrationCredential.parse_raw(data)
         jcred=json.loads(data)

         if len(get_user_model().objects.filter(username=jcred['username']))>0: #If the user already exists
            assert jcred['username']==req.user.username
            assert req.user.is_authenticated

         challenge=b64dec(req.session[SESSION_WEBAUTHN_CHALLENGE]) #Due to 
         origin=getattr(settings, 'WEBAUTHN_RP_ID', 'webframe.kenson.idv.hk')
         vr=verify_registration_response(credential=cred, expected_challenge=challenge, expected_origin="https://{0}".format(origin), expected_rp_id=origin, require_user_verification=True)
         vr=json.loads(options_to_json(vr))
         logger.debug('VerifiedRegistrationResponse: {0}'.format(vr))
         u, created=get_user_model().objects.get_or_create(username=jcred['username'])
         if created: 
            logger.info('The new user account was created: {0}'.format(u.username))
            if hasattr(settings, 'WEBAUTHN_INIT_USER_GROUPS'):
               for gp in getattr(settings, 'WEBAUTHN_INIT_USER_GROUPS'):
                  logger.info('Adding user[{0}] to group[{1}]...'.format(u.username, gp))
                  try:
                     u.groups.add(Group.objects.get(name=gp))
                  except Group.DoesNotExist:
                     logger.warning('Cannot found the group: {0}'.format(gp))
            if hasattr(settings, 'WEBAUTHN_INIT_USER_PERMISSIONS'):
               for perm in getattr(settings, 'WEBAUTHN_INIT_USER_PERMISSIONS'):
                  logger.info('Granting permission[{0}] to user:{1}...'.format(perm, u.username))
                  try:
                     u.user_permissions.add(Permission.objects.get(codename=perm))
                  except Permission.DoesNotExist:
                     logger.warning('Cannot found the permission: {0}'.format(perm))
         try:
            t=WebAuthnPubkey.objects.get(owner=u, id=vr['credentialId'])
         except WebAuthnPubkey.DoesNotExist:
            logger.debug('Created new pubkey for user:{0} -- {1}'.format(u.username, vr['credentialPublicKey']))
            t=WebAuthnPubkey(id=vr['credentialId'])
         t.owner=u
         t.pubkey=vr['credentialPublicKey']
         t.tipe=vr['credentialDeviceType']
         t.signCount=vr['signCount']
         t.displayName=jcred['displayName']
         t.save()
         result['verified']=True
         result['credentalId']=t.id
      except:
         result['verified']=False
         err=sys.exc_info()[1]
         result['error']=str(err.__class__.__name__)
         result['message']=err.args[0]
         logger.warning('Unexpected error', exc_info=True)
      finally:
         if SESSION_WEBAUTHN_CHALLENGE in req.session: del req.session[SESSION_WEBAUTHN_CHALLENGE]
         rep.write(json.dumps(result))
      return rep

class WebAuthnAuthentication( View ):
   def get(self, req):
      params=dict()
      rep=HttpResponse()
      if req.headers.get('Accept')=='application/json':
         rep.headers['Content-Type']='application/json'
         from webauthn import generate_authentication_options, options_to_json, base64url_to_bytes as b64bytes
         from webauthn.helpers.structs import UserVerificationRequirement, PublicKeyCredentialDescriptor
         allowedCredentials=None
         if 'username' in req.GET:
            allowedCredentials=list()
            u=User.objects.filter(username=req.GET['username'])
            if len(u)==1:
               for pubkey in WebAuthnPubkey.objects.filter(owner=u[0]):
                  logger.debug('Allowed Credential: {0}'.format(pubkey.id))
                  allowedCredentials.append(PublicKeyCredentialDescriptor(id=b64bytes(pubkey.id)))
            else:
               raise RuntimeError('Cannot found the exatcly user: {0}'.format(req.GET['username']))
         opts = generate_authentication_options(
              rp_id=getattr(settings, 'WEBAUTHN_RP_ID', 'webframe.kenson.idv.hk')
            , allow_credentials=allowedCredentials
            , user_verification=UserVerificationRequirement.REQUIRED
         )
         req.session[SESSION_WEBAUTHN_CHALLENGE]=b64enc(opts.challenge).decode('utf-8')
         rep.write(options_to_json(opts))
         return rep
      rep.status_code=405
      rep.write('Unsupported Content-Type: {0}'.format(req.headers.get('Accept', 'text/html')))
      return rep

   @transaction.atomic
   def post(self, req):
      rep=HttpResponse()
      rep.headers['Content-Type']='application/json'
      result=dict()
      try:
         from webauthn import verify_authentication_response, options_to_json, base64url_to_bytes as b64bytes
         from webauthn.helpers.structs import AuthenticationCredential
         logger.debug(req.body)
         challenge=b64dec(req.session[SESSION_WEBAUTHN_CHALLENGE])
         pubkey=WebAuthnPubkey.objects.get(id=json.loads(req.body.decode('utf-8'))['id'])
         origin=getattr(settings, 'WEBAUTHN_RP_ID', 'webframe.kenson.idv.hk')
         if not origin.startswith('http'): origin='https://{0}'.format(origin)
         verification = verify_authentication_response(
            credential=AuthenticationCredential.parse_raw(req.body),
            expected_challenge=challenge,
            expected_rp_id=getattr(settings, 'WEBAUTHN_RP_ID', 'webframe.kenson.idv.hk'),
            expected_origin=origin,
            credential_public_key=b64bytes(pubkey.pubkey),
            credential_current_sign_count=pubkey.signCount,
            require_user_verification=True,
         )
         logger.debug('Verificated!!!')
         pubkey.lastSignin=datetime.now()
         pubkey.save()
         auth_login(req, pubkey.owner)
         logger.debug('Saved the login into session!')
         result['verified']=True
      except WebAuthnPubkey.DoesNotExist:
         result['verified']=False
         result['error']='credential not found'
         result['message']='The specified credential not found, please register before login'
      except Exception as err:
         result['verified']=False
         logger.debug('Unexpected error', exc_info=True)
      finally:
         if SESSION_WEBAUTHN_CHALLENGE in req.session: del req.session[SESSION_WEBAUTHN_CHALLENGE]
         rep.write(json.dumps(result))
      return rep

class WebAuthnPubkeysView( LoginRequiredMixin, View ):
   def get(self, req):
      params=dict()
      params['target']=WebAuthnPubkey.objects.filter(owner=req.user).order_by('cb')
      params['target']=WebAuthnPubkeyTable(WebAuthnPubkey.objects.filter(owner=req.user))
      rc=RequestConfig(req)
      rc.configure(params['target'])
      return render(req, getattr(settings, 'TMPL_PUBKEYS', 'webframe/pubkeys.html'), params)

class WebAuthnPubkeyView( LoginRequiredMixin, View ):
   @transaction.atomic
   def delete(self, req, *args, **kwargs):
      logger.warning('Deleteing WebAuthnPubkey: {0}'.format(kwargs['id']))
      webpubkey=getObj(WebAuthnPubkey, id=kwargs['id'])
      webpubkey.delete()
      rep=HttpResponse()
      rep.headers['Content-Type']='text/json'
      rep.write(json.dumps({'result': True}))
      return rep
      
def logout(req):
   '''
   Logout the session.
   '''
   return Login().delete(req)

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
      root=MenuItem(name='/', label=_('appName'), props={'href': 'index'})
      root.save()
      lm=MenuItem(name='/L', parent=root)
      lm.save()
      lroot=MenuItem(name='/L/Root', label='Goto Root', parent=lm, props={'href': 'index'})
      lroot.save()
      rm=MenuItem(name='/R', parent=root, props={'class': 'navbar-right'})
      rm.save()
      lang=MenuItem(name='/R/locale', parent=rm, icon='fa-globe')
      lang.save()
      hi=MenuItem(name='/R/Hi', parent=rm, label='Hi, {username}')
      hi.save()
      register=MenuItem(name='/R/Hi/register', parent=hi, label='register', props={'href': reverse('webframe:webauthn-register')})
      register.save()
      logout=MenuItem(name='/R/Hi/Logout', parent=hi, label='Logout', props={'href': reverse('webframe:logout')})
      logout.save()
      activate('en')
      en=MenuItem(name='/R/locale/en', parent=lang, label=_('english'), props={'href':reverse('index')})
      en.save()
      activate('zh-hant')
      zht=MenuItem(name='/R/locale/zht', parent=lang, label=_('zh-hant'), props={'href':reverse('index')})
      zht.save()
      return redirect('admin:webframe_menuitem_changelist')
   return HttpResponseForbidden()

class WhoAmIView(APIView):
   authentication_classes = [authentication.TokenAuthentication, authentication.SessionAuthentication]
   permission_classes = [permissions.IsAuthenticated]
   
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
         lhs.childs=[hlp, ]
         if req.user.is_staff or req.user.is_superuser: 
            adm=MenuItem(parent=lhs, label='Admin Tools', icon='fa-cogs', props={'href': reverse('admin:index')})
            lhs.childs.append(adm)
         rst.childs=[lhs,]
         return Response(MenuItemSerializer(rst).data)

class ResetPasswordView(View):
   def get(self, req):
      params=dict()
      params['passwordReseted']=req.session.pop('reset-password', False)
      try:
         token=ResetPassword.objects.get(key=req.GET.get('token', None))
         if str(token.user.id)!=req.GET.get('uid'): raise get_user_model().DoesNotExist
         if token.isDead(): raise IndexError
         params['token']=token
      except ResetPassword.DoesNotExist:
         if 'token' in req.GET: messages.info(req, _('ResetPassword.tokenNotFound'))
      except get_user_model().DoesNotExist:
         messages.info(req, _('ResetPassword.userNotFound'))
      except IndexError:
         messages.info(req, _('ResetPassword.notEffective'))
      except:
         logger.exception('Unexpected error')
      return render(req, getattr(settings, 'TMPL_RESET_PASSWORD', 'webframe/resetPassword.html'), params)

   def post(self, req):
      if 'token' in req.POST:
         return self._step2(req)
      else:
         return self._step1(req)

   def _step1(self, req):
      # Initializes
      params=dict()
      username=req.POST.get('username')
      User=get_user_model()
      user=None
      ipAddr=getClientIP(req)

      # Getting target user
      try:
         user=User.objects.get(username=username)
      except User.DoesNotExist:
         try:
            user=User.objects.get(email=username)
         except User.DoesNotExist:
            messages.warning(req, _('Cannot found the user: %(username)s')%{'username':username})
            return redirect('webframe:resetPassword')

      # Security check: repeating reset
      requested=ResetPassword.objects.filter(request_by=ipAddr, cd__gte=getTime(datetime.now(), offset='-1H')).count()
      logger.warning(lm('ResetPassword: There have {count} time(s) requested within 1 hour', count=requested))
      if requested >= 5:
         messages.warning(req, _('Too many times to reset password'))
         return redirect('webframe:resetPassword')

      # Sending reset email
      with transaction.atomic():
         ResetPassword.objects.filter(user=user, enabled=True).update(enabled=False) #Invalid previous token
         reset=ResetPassword(user=user, request_by=ipAddr)
         reset.save()
         tmpl=Preference.objects.pref('TMPL_RESET_PASSWORD', defval='<p>Dear {user.first_name} {user.last_name},</p><p>Please click the link to reset your password: <a href="{absolute_url}{url}?uid={user.id}&token={token}" target="_blank">{absolute_url}{url}?uid={user.id}&token={token}</a>.</p>')
         subj=Preference.objects.pref('TMPL_RESET_PASSWORD_SUBJECT', defval=_('resetPassword'))
         sender=Preference.objects.pref('EMAIL_FROM', defval='info@kenson.idv.hk')
         tmpl=tmpl.format(user=user, absolute_url=getAbsoluteUrl(req), token=reset.key, url=reverse('webframe:resetPassword'))
         if user.email:
            sendEmail.delay(sender=sender, subject=subj, recipients=user.email, content=tmpl)
            email='{0}***{1}'.format(user.email[0:3], user.email[-7:])
            messages.info(req, _('The reset password instruction has been email to %(email)s. Please follow the instruction to reset your password')%{'email': user.email} )
         else:
            messages.info(req, _('You didn\'t setup an email in the system. Please contact your system-administrator and let them known your username and the reference number: %(id)s')%{'id': reset.id.hex[0:8]})
      return redirect('webframe:resetPassword')

   def _step2(self, req):
      params=dict()
      try:
         token=getObj(ResetPassword, key=req.POST.get('token', None))
         if str(token.user.id)!=req.GET.get('uid'): raise get_user_model().DoesNotExist
         if token.isDead(): raise IndexError
         passwd=req.POST.get('password', datetime.now())
         again=req.POST.get('passwordAgain', 'Abc123$%^')
         if passwd!=again: raise ValueError
         with transaction.atomic():
            token.user.set_password(passwd)
            token.user.save()
            token.complete_date=datetime.now()
            token.complete_by=getClientIP(req)
            token.enabled=False
            token.save()
            messages.info(req, _('The password has been updated successfully.'))
            tmpl=Preference.objects.pref('TMPL_RESETED_PASSWORD', defval='<p>Dear {user.first_name} {user.last_name},</p>i<p>Your password has been updated successfully.</p>')
            subj=Preference.objects.pref('TMPL_RESET_PASSWORD_SUBJECT', defval=_('resetPassword'))
            sender=Preference.objects.pref('EMAIL_FROM', defval='info@kenson.idv.hk')
            tmpl=tmpl.format(user=token.user, absolute_url=getAbsoluteUrl(req), token=token.key, url=reverse('webframe:resetPassword'))
            sendEmail.delay(sender=sender, subject=subj, recipients=token.user.email, content=tmpl)
            req.session['reset-password']=True
      except ResetPassword.DoesNotExist:
         messages.info(req, _('ResetPassword.tokenNotFound'))
      except get_user_model().DoesNotExist:
         messages.info(req, _('ResetPassword.userNotFound'))
      except IndexError:
         messages.info(req, _('ResetPassword.notEffective'))
      return redirect('webframe:resetPassword')

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
   ''' Login the user and register the AuthToken '''

   def post(self, req):
      logger.warning('Content-Type: %s'%req.headers.get('Content-Type'))
      if req.headers.get('Content-Type', 'application/x-www-form-urlencoded').startswith('application/json'):
         params=json.loads(req.body)
      else:
         params=req.POST
      username=params.get('username', None)
      password=params.get('password', None)
      deviceName=params.get('deviceName', None)
      try:
         if not username: raise ValueError('username is None')
         if not password: raise ValueError('password is None')
         if not deviceName: raise ValueError('deviceName is None')
         user=Login().login(req, username, password)
         if not user: raise PermissionDenied()
         logger.info('Got the loging: %s'%user.username)
      except PermissionDenied:
         raise
      except:
         logger.debug('', exc_info=True)
         user=None
         raise PermissionDenied()
      
      try:
         token=Token.objects.get(user=user)
         created=False
         tokenDetail=TokenDetail.objects.get(token=token)
         if not tokenDetail: raise TokenDetail.DoesNotExist
      except Token.DoesNotExist:
         token=Token.objects.create(user=user)
         created=True
         tokenDetail=TokenDetail(token=token, name=deviceName)
         tokenDetail.save()
      except TokenDetail.DoesNotExist:
         tokenDetail=TokenDetail(token=token, name=deviceName)
         tokenDetail.save()
      logger.debug({'token': token.key, 'status': 'created' if created else 'retrieved', 'deviceName': deviceName, 'username':user.username})
      return JsonResponse({'token': 'ENC:{0}'.format(token.key[::-1]), 'status': 'created' if created else 'retrieved', 'username':user.username})
