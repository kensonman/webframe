from django.conf import settings


def absolute_path(req):
	'''
	Get the absolute-path of the application or request
	'''
	ATTR='ABSOLUTE_PATH'
	RST={ATTR: None}
	if hasattr(settings, ATTR) and getattr(settings, ATTR, False):
		RST[ATTR]=getattr(settings, ATTR)
	else:
		RST[ATTR]=req.get_host()
	return RST
