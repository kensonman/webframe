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
	end=5
	return '%s...%s'%(value[0:beg], value[end*-1:])

@register.filter
def replaceNewline(value, replacement=''):
   '''
   Replace all new line character to specified replacement. Default is ''.

   It will detect the '\r\n' or '\n\r', and replace with replacement once only.

   e.g.:
      'Line 1\nLine 2\rLine 3'|replaceNewline => 'Line 1Line 2Line 3'
      'Line 1\nLine 2\rLine 3'|replaceNewline:'+' => 'Line 1+Line 2+Line 3'
      'Line 1\r\nLine 2\r\nLine 3'|replaceNewline:'+' => 'Line 1+Line 2+Line 3'
   '''
   import re
   v=re.sub(r'\r\n', '\n', value)
   v=re.sub(r'\n\r', '\n', value)
   return re.sub(r'[\n\r]', replacement, v)
