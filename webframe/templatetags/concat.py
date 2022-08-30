from django import template
register=template.Library()

@register.filter
def concat(str1, str2):
	'''
	Concat two object in string
	'''
	str1=str(str1)
	str2=str(str2)
	return '%s%s'%(str1, str2)
