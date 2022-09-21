from django import template
from base64 import b64encode, b64decode

register=template.Library()

@register.filter
def base64e(val):
   '''
   Enclose a string into base64
   '''
   return b64encode(str(val).encode('utf-8')).decode('utf-8')

@register.filter
def base64d(val):
   '''
   Decode a base64 string
   '''
   return b64decode(str(val).encode('utf-8')).decode('utf-8')
