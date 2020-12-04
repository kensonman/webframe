from django import template
import mimetypes, os
register=template.Library()

@register.filter
def mime(value):
   '''
   Retrieve/Guess the mime-type from filename.

   USAGE
   =====
   {{'path/to/image.gif'|mime}} => "image/gif"
   {{'path/to/video.mp4'|mime}} => "video/mp4"
   {{'path/to/unknown.abcdefg'|mime}} => "abcdefg"
   '''
   try:
      return mimetypes.guest_type(value, strict=True)
   except:
      return os.path.splitext(value)[1][1:]
