from django import template
try:
   from django.urls import reverse, NoReverseMatch
except ImportError:
   from django.core.urlresolvers import reverse, NoReverseMatch 
from django.template.defaultfilters import stringfilter

register=template.Library()

@register.filter
@stringfilter
def urlexists(url):
   '''
   Check the URL is registered in the urls.py.
   Usage: 
       <url-name>|urlexists  
   '''
   try:
      rst=reverse(url)
      return True
   except NoReverseMatch as ex:
      if ex.args[0].find('pattern(s) tried')>0: #If tried pattern, but parameter not match
         return True
      return False
