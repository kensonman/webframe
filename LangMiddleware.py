from django.conf import settings
from django.utils.translation import LANGUAGE_SESSION_KEY
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
         lang=req.session.get(LANGUAGE_SESSION_KEY, getattr(settings, 'LANGUAGE_CODE', None))
         if req.method=='GET' and 'lang' in req.GET:
            lang=req.GET['lang']
         req.session[LANGUAGE_SESSION_KEY]=lang
else:
   class LangMiddleware(object):
      def __init__(self, get_response):
         self.get_response=get_response

      def __call__(self, req):
         '''
         Get the lang information from req.GET or settings, then inject into the session
         '''
         lang=req.session.get(LANGUAGE_SESSION_KEY, getattr(settings, 'LANGUAGE_CODE', None))
         if req.method=='GET' and 'lang' in req.GET:
            lang=req.GET['lang']
         req.session[LANGUAGE_SESSION_KEY]=lang
         
         return self.get_response(req)
