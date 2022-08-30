from django import template
from django.core.files.images import get_image_dimensions
import mimetypes, os, logging
register=template.Library()

def __dimension__(value):
   return get_image_dimensions(value)

@register.filter
def imgwidth(value):
   '''
   Retrieve the width of the specified image.

   USAGE
   =====
   {{fieldField.file|imgwidth}}
   '''
   try:
      return __dimension__(value)[0]
   except:
      logging.getLogger('webframe.templatetags.img').exception('Unexpected exception')
      return 1

@register.filter
def imgheight(value):
   '''
   Retrieve the width of the specified image.

   USAGE
   =====
   {{fieldField.file|imgheight}}
   '''
   try:
      return __dimension__(value)[1]
   except:
      logging.getLogger('webframe.templatetags.img').exception('Unexpected exception')
      return 1
