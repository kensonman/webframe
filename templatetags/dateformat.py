from django import template
register=template.Library()

@register.filter
def dateformat(value, fmt):
	'''
	Convert the date-format between date.js and python
	'''
	try:
		value=value.replace('%','')
		return value
	except ValueError:
		pass
	return None
