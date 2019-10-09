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
         rst=value.get(key)
      elif hasattr(value, '__getitem__'):
         rst=value.__getitem__(key)
      else:
         rst=str(value)[key]
      return str(rst)
   except ValueError:
      pass
   return None
