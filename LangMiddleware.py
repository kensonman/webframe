from django.conf import settings
from django.utils import translation
import django, logging

logger=logging.getLogger('webframe.middlewares.LangMiddleware')


class LangMiddleware(object):
   '''
   Inject the lang information into session
   '''
   def __init__(self, get_response):
      self.get_response=get_response

   def __call__(self, req):
      '''
      Get the lang information from req.GET or settings, then inject into the session
      '''
      lang=translation.get_language_from_request(req)
      logger.debug('Supported: %s'%req.META.get('HTTP_ACCEPT_LANGUAGE', None))
      #lang=req.session.get(translation.LANGUAGE_SESSION_KEY, getattr(settings, 'LANGUAGE_CODE', None))
      logger.debug('User Lang: %s'%lang)
      if req.method=='GET' and 'lang' in req.GET:
         lang=req.GET['lang']
      if hasattr(settings, 'FORCE_LANGUAGE_CODE'):
         if 'HTTP_ACCEPT_LANGUAGE' in req.META:
            del req.META['HTTP_ACCEPT_LANGUAGE']
         lang=getattr(settings, 'FORCE_LANGUAGE_CODE')
      
      logger.debug('Finially Lang: %s'%lang)
      req.session[translation.LANGUAGE_SESSION_KEY]=lang
      translation.activate(lang)
      req.LANGUAGE_CODE=translation.get_language()
      
      rep=self.get_response(req)

      translation.deactivate()

      return rep

   # Backward compatibility django 1.9 or older
   def process_request(self, req):
      return self.__call__(req)
