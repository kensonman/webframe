from django import template
from django.contrib.auth.models import User, AnonymousUser
from django.utils.functional import SimpleLazyObject
from webframe.models import Preference
from webframe.CurrentUserMiddleware import get_current_user
import logging

logger=logging.getLogger('webframe.templatetags')

register=template.Library()

@register.filter
def calc(value, formula):
   '''
   Execute the math calculation.

   Let x=7, given example:
      {{x|calc:'{}*-1'}}   => return -7
      {{x|calc:'{}/0'}}    => return "{integer division or modulo by zero}"
      {{x|calc:''}}        => return "{SyntaxError: unexpected EOF while parsing}"
   '''
   try:
      return eval(formula.format(value))
   except:
      import os
      return '{{{0}}}'.format(os.exc_info()[1])

@register.simple_tag(name='set')
def setTag(value):
   '''
   Execute the math calculation.

   Let x=7, given example:
      {%set x|calc:'{}*-1'%}  => return -7
      {%set x|calc:'{}/0'%}   => return "{integer division or modulo by zero}"
      {%set x|calc:'{}/0'%}   => return "{SyntaxError: unexpected EOF while parsing}"
   '''
   return value
