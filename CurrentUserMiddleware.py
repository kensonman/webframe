#
# URL: https://blndxp.wordpress.com/2016/03/04/django-get-current-user-anywhere-in-your-code-using-a-middleware/
#
import django

VAR_REQUEST='request'
VAR_USER='user'

try:
   from threading import local
except ImportError:
   from django.utils._threading_local import local

_thread_locals = local()

def get_current_request():
   """ returns the request object for this thread """
   return getattr(_thread_locals, VAR_REQUEST, None)

def get_current_user():
   """ returns the current user, if exist, otherwise returns None """
   request = get_current_request()
   if request:
      return getattr(request, VAR_USER, None)
   return None


if django.VERSION[1]<10:
   class CurrentUserMiddleware(object):
      '''
      The middleware to put the current user into local-thread
      '''

      def process_request(self, req):
         '''
         Handling the request
         '''
         _thread_locals.request = req 

      def process_response(self, request, response):
         '''
         Remove the local variable from ram
         '''
         if hasattr(_thread_locals, VAR_REQUEST):
            del _thread_locals.request
         return response
else:
   class CurrentUserMiddleware(object):
      '''
      The middleware to put the current user into local-thread
      '''
      def __init__(self, get_response):
         self.get_response=get_response

      def __call__(self, req):
         '''
         Handling the request
         '''
         _thread_locals.request = req 

         rep=self.get_response(req)

         '''
         Remove the local variable from ram
         '''
         if hasattr(_thread_locals, VAR_REQUEST):
            del _thread_locals.request
         return rep 

