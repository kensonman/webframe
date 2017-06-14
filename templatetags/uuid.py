# -*- coding: utf-8 -*-
# 
# File: uuid.py
# Author: Kenson Man <kenosn.idv.hk@gmail.com>
# Desc: The template-tag used to generate a uuid into output.
# Sample:
#    {%uuid%}        # Generate a UUID and output
#    {%uuid as abc%} # Generate a UUID and store into abc
#
from django.template import Library, Node, TemplateSyntaxError
from uuid import uuid4

register = Library()

@register.simple_tag(name='uuid')
def do_uuid():
   """
   Desc: The template-tag used to generate a uuid into output.
   Sample:
      {%uuid%}        # Generate a UUID and output
      {%uuid as abc%} # Generate a UUID and store into abc
   """
   return uuid4().hex

