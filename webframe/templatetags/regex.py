from django import template
import re, logging
register=template.Library()

@register.filter
def match(value, regex=r'^.*$'):
   '''
   Return the first match object according to specified regex.
   '''
   try:
      if regex:
          return re.compile(regex).match(value)
   except:
      logger=logging.getLogger('webframe.templatetags.regex')
      logger.exception('Unexpected exception')
      logger.debug('where value is following')
      logger.debug(value)
   return value
