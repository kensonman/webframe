from django import template
register=template.Library()

@register.filter
def stringformat(value, fmt='{}'):
   '''
   format the value
   '''
   try:
      if isinstance(value, dict):
         return fmt.format(**value)
      return fmt.format(value)
   except:
      return 'Value[%s]::%s cannot format by pattern: %s'%(value, type(value).__name__, fmt)
