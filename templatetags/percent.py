from django import template
register=template.Library()

@register.filter
def percent(value, base=100):
   return int((int(value)/base)*100)
