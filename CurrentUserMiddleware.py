from threading import local

class CurrentUserMiddleware(object):
	'''
	The middleware to put the current user into local-thread
	'''

	def process_request(self, user):
		'''
		Handling the request
		'''
		thread=local()
		thread.user=req.user
