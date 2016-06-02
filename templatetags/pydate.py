from django import template
from django.template.defaultfilters import date
register=template.Library()

def stftime2django(fmt):
	'''
	Due to the datetime.strftime cannot use the local in django,
	modify the code to convert datetime.strftime to the django date filter style.

	Unsupported Format (Due to the difference between strftime and date-filter):
		%c - Locale’s appropriate date and time representation.
		%x - Locale’s appropriate date representation.
		%X - Locale’s appropriate time representation.
	'''
	result=''
	pos=0
	while(pos<len(fmt)):
		ch=fmt[pos]
		pos+=1
		
		if ch=="%":
			ch=fmt[pos]
			pos+=1
			if ch=='b': 
				ch='N'
			elif ch=='B': 
				ch='F'
			elif ch=='I': 
				ch='h'
			elif ch=='p':
				ch='A'
			elif ch=='M':
				ch='i'
			elif ch=='S':
				ch='s'
			elif ch=='f':
				ch='u'
			elif ch=='z':
				ch='Z'
			elif ch=='Z':
				ch='T'
			elif ch=='j':
				ch='z'
			elif ch=='U':
				ch='W'
			result+=ch
		else:
			result+="\\%s"%ch
	return result


@register.filter
def pydate(value, fmt=None):
	'''
	Parsing the date into string according to the strftime format
	'''
	try:
		if not fmt: fmt='%Y-%m-%d %H:%M:%S'
		if not value: return ''
		#2016-04-07 10:51, Kenson
		#Convert the date filter format due to the strftime cannot use the django locale
		fmt=stftime2django(fmt)
		if hasattr(value, 'strftime'):
			return date(value, fmt)
		else:
			return 'No strftime'
	except ValueError:
		pass
	return 'Error'
