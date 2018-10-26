# -*- coding: utf-8 -*-
# File: webframe/decorators.py
# Author: Kenson Man
# Date: 2018-09-22 10:48
# Desc: provide the decorators in webframe
from django.http import HttpRequest
from .functions import getBool
from .models import *

class is_enabled(object):
   def __init__(self, pref_name, defval=True):
      self.pref_name=pref_name
      self.defval=defval

   def __call__(self, func):
      def wrapper(*args, **kwargs):
         u=None
         if len(args)>0:
            if isinstance(args[0], HttpRequest):
               u=args[0].user
         enabled=getBool(Preference.objects.pref(self.pref_name, user=u, returnValue=True, defval=self.defval))
         if not enabled:
            raise NotImplementedError('The function has been disabled by Preference: %s'%self.pref_name)
         return func(*args, **kwargs)
      return wrapper
         
         
