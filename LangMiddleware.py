from django.conf import settings
from django.utils.translation import LANGUAGE_SESSION_KEY

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
