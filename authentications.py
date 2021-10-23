# -*- coding: utf-8 -*-
# File:     webframe/authentications.py
# Author:   Kenson Man <kenson@atomsystem.com.hk>
# Date:     2021-03-07 12:36
# Desc:     Provide the customized AuthenticationBackend, which will take care of the effective period when authenticate(req, username, password)
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model as usermodel
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import *
from django.contrib.auth.signals import user_logged_in
from django.db.models import Q
from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _, ugettext as __
from django.utils import timezone as tz
from webframe.functions import getBool
from webframe.models import Preference, Profile
import logging

logger=logging.getLogger('webframe.authentications')

class AuthenticationBackend(ModelBackend):
   '''
   The authentication backend that including the effective period checking. Due to the default authentication backend (Django provided) does not include the effective period checking. 

   This authentication backend will also **ignore** the case of username.

   USAGE
   ====

   ```Python
   # proj/settings.py
   AUTHENTICATION_BACKENDS = [
      'webframe.authentications.AuthenticationBackend'
   ]
   AUTHENTICATION_BACKEND_CASE_INSENSITIVE = True #Set to Fase if you want case-sensitive
   ```
   '''
   def __init__(self):
      pass
   
   def authenticate(self, req, username=None, password=None):
      '''Handling the authentication'''
      messages.get_messages(req).used=True
      try:
         if getattr(settings, 'AUTHENTICATION_BACKEND_CASE_INSENSITIVE', True):
            logger.warning('B4 case-insensitive: {0}'.format(username))
            username=usermodel()._default_manager.get(username__iexact=username).get_username()
            logger.warning('AF case-insensitive: {0}'.format(username))
         user=super().authenticate(req, username=username, password=password)
         if user:
            if user.is_superuser and user.is_active: 
               logger.debug('Ignore effective period checking for active superuser: {0}'.format(user.username))
            else:
               now=datetime.utcnow().replace(tzinfo=utc)
               try:
                  prof=Profile.objects.get(user=user)
                  if not pref.alive:
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
      except User.DoesNotExist:
         logger.debug('Invalid username/password, {0}/{1}'.format(username, password))
         messages.info(req, _('invalid username or password'))
         return None
      except:
         logger.exception('Unexpected exception when authenticate the user: {0}'.format(username))

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
