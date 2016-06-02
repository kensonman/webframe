from django import template
register=template.Library()

@register.filter
def trim(value, length=10):
	'''
	Trim the value into specific length
	'''
	if value:
		value=str(value)
	else:
		value=''
	if len(value)<length: return value
	beg=int(length/2)
	end=int((length-3)/2)
	return '%s...%s'%(value[0:beg], value[end*-1])
