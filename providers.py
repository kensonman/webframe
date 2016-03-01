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
	Inject the TMPL_BASE, TMPL_HEADER, TMPL_FOOTER and TMP_PAGINATION settings into the request
	'''
	RST={
		'TMPL_BASE': getattr(settings, 'TMPL_BASE', 'webframe/framework.html'),
		'TMPL_HEADER': getattr(settings, 'TMPL_HEADER', 'webframe/header.html'),
		'TMPL_FOOTER': getattr(settings, 'TMPL_FOOTER', 'webframe/footer.html'),
		'TMPL_PAGINATION': getattr(settings, 'TMPL_PAGINATION', 'webframe/pagination.html'),
	}
	return RST

def fmt_injection(req):
	'''
	Inject the FMT_DATE, FMT_TIME and FMT_DATETIME into the request
	'''
	RST={}
	RST['FMT_DATE']= getattr(settings, 'FMT_DATE', '%Y-%m-%d')
	RST['FMT_TIME']= getattr(settings, 'FMT_TIME', '%Y-%m-%d')
	RST['FMT_DATETIME']= getattr(settings, 'FMT_DATETIME', '%s %s'%(RST['FMT_DATE'], RST['FMT_TIME']))
	return RST
