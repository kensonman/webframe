# -*- coding: utf-8 -*-
# Date:   2018-08-08 09:22
# Author: Kenson Man <kenson@kenson.idv.hk>
# File:   NextURLMiddleware.py
# Desc:   Create the middleware to intercept request when GET. When it's contains the NEXT_URL_PARAM (default is "next") in the session,
#         do nothing and return the URL redirect.
#
from django.conf import settings
from django.shortcuts import redirect
import logging

class NextURLMiddleware(object):

   def __init__(self, get_response):
      self.get_response=get_response
      self.NEXT_URL_PARAM=getattr(settings, 'NEXT_URL_PARAM', 'next')
      self.logger=logging.getLogger('webframe.NextURLMiddleware')

   def __call__(self, req):
      if req.method=='GET':
         next=req.session.get(self.NEXT_URL_PARAM, None)
         if next: 
            del req.session[self.NEXT_URL_PARAM] #Remove and reset the session
            self.logger.debug('Redirect to session[\'{0}\']: {1}'.format(self.NEXT_URL_PARAM, next))
            return redirect(next)

      rep=self.get_response(req)
      return rep
