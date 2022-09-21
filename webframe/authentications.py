# -*- coding: utf-8 -*-
# File:     webframe/authentications.py
# Author:   Kenson Man <kenson@atomsystem.com.hk>
# Date:     2021-03-07 12:36
# Desc:     Provide the customized AuthenticationBackend, which will take care of the effective period when authenticate(req, username, password)
from base64 import b64encode as b64enc, b64decode as b64dec
from datetime import datetime
from deprecation import deprecated
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model as usermodel
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import *
from django.contrib.auth.signals import user_logged_in
from django.db.models import Q
from django.utils.timezone import utc
from django.utils.translation import gettext_lazy as _, ugettext as __
from django.utils import timezone as tz
from .functions import getBool, getClientIP
from .models import Preference, Profile, WebAuthnPubkey
import logging, json

logger=logging.getLogger('webframe.authentications')
SESSION_WEBAUTHN_CHALLENGE='webauthn-challenge'

class EffectiveUserAuthenticationBackend(ModelBackend):
   '''
   The authentication backend that including the effective period checking. 
   Due to the default authentication backend (Django provided) does not include the effective period checking. 

   USAGE
   ====

   ```Python
   # proj/settings.py
   AUTHENTICATION_BACKENDS = [
      'webframe.authentications.EffectiveUserAuthenticationBackend'
   ]
   AUTHENTICATION_BACKEND_CASE_INSENSITIVE = True #Set to Fase if you want case-sensitive
   ```
   '''
   def __init__(self):
      pass
   
   def authenticate(self, req, username=None, password=None):
      '''Handling the authentication'''
      logger.warning('EffectiveUserAuthenticationBackend invoked')
      messages.get_messages(req).used=True
      try:
         if getattr(settings, 'AUTHENTICATION_BACKEND_CASE_INSENSITIVE', True):
            logger.warning('B4 case-insensitive: {0}'.format(username))
            username=usermodel()._default_manager.get(username__iexact=username).get_username()
            logger.warning('AF case-insensitive: {0}'.format(username))
         user=super().authenticate(req, username=username, password=password)
         return self.check_effective(user)
      except User.DoesNotExist:
         logger.debug('Invalid username/password, {0}/{1}'.format(username, password))
         messages.info(req, _('invalid username or password'))
         return None
      except:
         raise RuntimeError('Unexpected exception when authenticate the user: {0}'.format(username), sys.exc_info()[1])

   def check_effective(self, user):
      if user:
         if user.is_superuser and user.is_active: 
            logger.debug('Ignore effective period checking for active superuser: {0}'.format(user.username))
         else:
            now=datetime.utcnow().replace(tzinfo=utc)
            try:
               prof=Profile.objects.get(user=user)
               if not prof.alive:
                  logger.debug('User<{0}> is not effective! {{effDate: {1}, expDate: {2}, now: {3}}}'.format(user.username, prof.effDate, prof.expDate, now))
                  messages.info(req, _('Your account is not effective'))
                  user=None
            except Profile.DoesNotExist:
               allow=getattr(settings, 'WF_ALLOW_USER_NO_PROFILE', True)
               if getBool(allow):
                  logger.warn('Ignored effective-period checking due to the specified user does\'not contains the profile: {0}'.format(username))
               else:
                  logger.warn('User<{0}> is not configured properly!'.format(user.username))
                  messages.info(req, _('Your account is not configured correctly'))
                  user=None
      if user:
         logger.info('User<{0}> was signed-in!'.format(user.username))
         #TODO: fire the signal here if necessary
         return user
      else:
         raise User.DoesNotExist

@deprecated(deprecated_in='2.12.4', details='Remained for backward compatibility. Use EffectiveUserAuthenticationBackend instead.')
class AuthenticationBackend(EffectiveUserAuthenticationBackend):
    pass

class WebAuthnBackend(ModelBackend):
   '''
   The authentication backend that used to support WebAuthn (password less) authentication according to FIDO2 standard.

   USAGE
   ====

   ```Python
   # proj/settings.py
   AUTHENTICATION_BACKENDS = [
      'webframe.authentications.WebAuthnBackend'
   ]
   WEBAUTHN_BACKEND_EFFECTIVE_ONLY=False #If want to allow ineffective user
   ```
   '''
   def __init__(self):
      pass

   def authenticate(self, req, cred=None):
      from webauthn import verify_authentication_response
      from webauthn import options_to_json
      from webauthn import base64url_to_bytes as b64bytes
      from webauthn.helpers.structs import AuthenticationCredential
      challenge=b64dec(req.session[SESSION_WEBAUTHN_CHALLENGE])
      pubkey=WebAuthnPubkey.objects.get(id=json.loads(cred.decode('utf-8'))['id'])
      origin=getattr(settings, 'WEBAUTHN_RP_ID', 'webframe.kenson.idv.hk')
      if not origin.startswith('http'): origin='https://{0}'.format(origin)
      verification = verify_authentication_response(
         credential=AuthenticationCredential.parse_raw(cred),
         expected_challenge=challenge,
         expected_rp_id=getattr(settings, 'WEBAUTHN_RP_ID', 'webframe.kenson.idv.hk'),
         expected_origin=origin,
         credential_public_key=b64bytes(pubkey.pubkey),
         credential_current_sign_count=pubkey.signCount,
         require_user_verification=True,
      )
      logger.debug('Verificated!!!')
      pubkey.lastSignin=datetime.now()
      pubkey.ipaddr=getClientIP(req)
      pubkey.save()

      if getBool(getattr(settings, 'WEBAUTHN_BACKEND_EFFECTIVE_ONLY', True)):
         return EffectiveUserAuthenticationBackend().check_effective(pubkey.owner)

      return pubkey.owner

   def get_user(self, user_id):
     return usermodel().objects.get(id=user_id)

class ActiveUserRequiredMixin(UserPassesTestMixin):
   def test_func(self):
      if not self.request: return False
      if not self.request.user: return False
      if not self.request.user.is_authenticated: return False
      if not self.request.user.is_active: return False

      try:
         pf=self.request.user.profile
         return pf.alive
      except Profile.DoesNotExist:
         #Ignore the checking
         pass
      return True
