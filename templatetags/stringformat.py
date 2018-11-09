from django import template
register=template.Library()

@register.filter
def stringformat(value, fmt='{}'):
   '''
   format the value
   '''
   if isinstance(value, dict):
      return fmt.format(**value)
   return fmt.format(value)
