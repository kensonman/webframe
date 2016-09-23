#
# URL: https://blndxp.wordpress.com/2016/03/04/django-get-current-user-anywhere-in-your-code-using-a-middleware/
#

try:
	from threading import local
except ImportError:
	from django.utils._threading_local import local

_thread_locals = local()

def get_current_request():
	""" returns the request object for this thread """
	return getattr(_thread_locals, "request", None)

def get_current_user():
	""" returns the current user, if exist, otherwise returns None """
	request = get_current_request()
	if request:
		return getattr(request, "user", None)
	return None

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
		if hasattr(_thread_locals, 'request'):
			del _thread_locals.request
		return response
