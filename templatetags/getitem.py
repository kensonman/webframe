from django import template
register=template.Library()

@register.filter
def getitem(value, key):
   try:
      if isinstance(value, str):
         value=eval(value)
   except:
      pass
   try:
      if hasattr(value, 'get'):
         return value.get(key)
      elif hasattr(value, '__getitem__'):
         return value.__getitem__(key)
   except ValueError:
      pass
   return None
