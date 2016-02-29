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

def template_injection(req):
	'''
	Inject the TMPL_* settings into the request
	'''
	RST={
		'TMPL_BASE': getattr(settings, 'TMPL_BASE', 'webframe/framework.html'),
		'TMPL_HEADER': getattr(settings, 'TMPL_HEADER', 'webframe/header.html'),
		'TMPL_FOOTER': getattr(settings, 'TMPL_FOOTER', 'webframe/footer.html'),
	}
	return RST
