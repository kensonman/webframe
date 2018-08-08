# -*- coding: utf-8 -*-
# Date:   2018-08-08 09:22
# Author: Kenson Man <kenson@kenson.idv.hk>
# File:   NextURLMiddleware.py
# Desc:   
#   The middleware to intercept request when method is "GET" and URL match with NEXT_URL_INTERCEPTION (default is '^/?$'). 
#   It will do nothing and return the URL redirect when URL is matched with one of NEXT_URL_INTERCEPTION (default is '^/?$').
#
from django.conf import settings
from django.shortcuts import redirect
import logging, re

class NextURLMiddleware(object):
   '''
   The middleware to intercept request when method is "GET" and URL match with NEXT_URL_INTERCEPTION (default is '^/?$'). 
   It will do nothing and return the URL redirect when URL is matched with one of NEXT_URL_INTERCEPTION (default is '^/?$').

   settings.py
   -----------
   NEXT_URL_PARAM='next'
   NEXT_URL_INTERCEPTION=['^/?$', ]
   '''

   def __init__(self, get_response):
      self.logger=logging.getLogger('webframe.NextURLMiddleware')
      self.get_response=get_response
      self.NEXT_URL_PARAM=getattr(settings, 'NEXT_URL_PARAM', 'next')
      self.NEXT_URL_INTERCEPTION=getattr(settings, 'NEXT_URL_INTERCEPTION', ['^/?$', ])

   def __call__(self, req):
      if req.method=='GET':
         for pattern in self.NEXT_URL_INTERCEPTION: 
            # Find the match pattern
            if re.match(pattern, req.get_full_path()):
               next=req.session.get(self.NEXT_URL_PARAM, None)
               if next: 
                  del req.session[self.NEXT_URL_PARAM] #Remove and reset the session
                  self.logger.debug('Redirect to session[\'{0}\']: {1}'.format(self.NEXT_URL_PARAM, next))
                  return redirect(next)
         #End-For
      #End if req.method=='GET'

      rep=self.get_response(req)
      return rep
