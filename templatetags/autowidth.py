from django import template
register=template.Library()

@register.filter
def autowidth(lst, total=100.0):
   if hasattr(lst, '__len__'): lst=lst.__len__()
   if not isinstance(lst, float): lst=float(lst)
   return round(total/lst, 1)
