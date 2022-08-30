from django import template
from webframe.functions import encrypt as efn, decrypt  as dfn

register=template.Library()

@register.filter
def encrypt(val):
   '''
   Encrypt the specified val with the default secret-key
   '''
   return efn(val)

@register.filter
def decrypt(val):
   '''
   Decrypt the specified val with the default secret-key
   '''
   return dfn(val)
