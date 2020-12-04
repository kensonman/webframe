from django import template
import re
register=template.Library()

@register.filter
def match(value, regex=r'^.*$'):
   '''
   Return the first match object according to specified regex.
   '''
   if regex:
       return re.compile(regex).match(value)
   return value
