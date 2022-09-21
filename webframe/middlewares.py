# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
import hashlib, logging

logger=logging.getLogger('webframe.middlewares.HeaderAuthenticationMiddleware')

class HeaderAuthenticationMiddleware(object):
   def __init__(self, get_response):
      self.get_response=get_response
      self.username=getattr(settings, 'HEADER_AUTHENTICATION_MIDDLEWARE_USERNAME', 'X-USERNAME')
      self.password=getattr(settings, 'HEADER_AUTHENTICATION_MIDDLEWARE_PASSWORD', 'X-PASSWORD')
      self.secret=getattr(settings, 'HEADER_AUTHENTICATION_MIDDLEWARE_SECRET', 'X-SECRET')
      self.key=getattr(settings, 'HEADER_AUTHENTICATION_MIDDLEWARE_KEY', 'r5fxh4CAZdmTzws5dZXF69dTeckq95ZL')

   def __call__(self, req):
      if self.username in req.headers and self.password in req.headers and self.secret in req.headers:
         logger.debug('Verifying the authentication...')
         passphrase='{0}:{1}-{2}'.format(req.headers[self.username], req.headers[self.password], self.key)
         m=hashlib.md5()
         m.update(passphrase.encode('utf-8'))
         if m.hexdigest()!=req.headers[self.secret]: return HttpResponseForbidden('Incorrect login information')
         u=authenticate(req, username=req.headers[self.username], password=req.headers[self.password])
         if u and u.is_active:
            login(req, u)
         else:
            return HttpResponseForbidden('Incorrect login information')
      else:
         logger.debug('Bypass {0}...'.format(self.__class__))

      rep=self.get_response(req)
      return rep
