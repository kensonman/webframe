from django import template
register=template.Library()

@register.filter
def stringformat(value, fmt='{}'):
   '''
   format the value
   '''
   return fmt.format(value)
