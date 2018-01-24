from django.conf import settings
from django.utils import translation
import django


if django.VERSION[1]<10:
   class LangMiddleware(object):
      '''
      Inject the lang information into session
      '''

      def process_request(self, req):
         '''
         Get the lang information from req.GET or settings, then inject into the session
         '''
         lang=req.session.get(translation.LANGUAGE_SESSION_KEY, getattr(settings, 'LANGUAGE_CODE', None))
         if req.method=='GET' and 'lang' in req.GET:
            lang=req.GET['lang']
         if hasattr(settings, 'FORCE_LANGUAGE_CODE'):
            if 'HTTP_ACCEPT_LANGUAGE' in req.META:
               del req.META['HTTP_ACCEPT_LANGUAGE']
            lang=getattr(settings, 'FORCE_LANGUAGE_CODE')

         req.session[translation.LANGUAGE_SESSION_KEY]=lang
         translation.activate(lang)
else:
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
         lang=req.session.get(translation.LANGUAGE_SESSION_KEY, getattr(settings, 'LANGUAGE_CODE', None))
         if req.method=='GET' and 'lang' in req.GET:
            lang=req.GET['lang']
         if hasattr(settings, 'FORCE_LANGUAGE_CODE'):
            if 'HTTP_ACCEPT_LANGUAGE' in req.META:
               del req.META['HTTP_ACCEPT_LANGUAGE']
            lang=getattr(settings, 'FORCE_LANGUAGE_CODE')

         req.session[translation.LANGUAGE_SESSION_KEY]=lang
         translation.activate(lang)
         
         return self.get_response(req)

