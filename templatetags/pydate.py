from django import template
register=template.Library()

@register.filter
def pydate(value, fmt=None):
	'''
	Parsing the date into string according to the strftime format
	'''
	try:
		if not fmt: fmt='%Y-%m-%d %H:%M:%S'
		if not value: return ''
		if hasattr(value, 'strftime'):
			return value.strftime(fmt)
		else:
			return 'No strftime'
	except ValueError:
		pass
	return 'Error'
