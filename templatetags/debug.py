from django import template

register = template.Library()

@register.filter
def fields(obj):
   return [(field.name, field.value_to_string(obj)) for field in obj._meta.fields]

@register.filter
def clazz(obj):
   return obj.__class__.__name__
