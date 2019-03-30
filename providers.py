from django.conf import settings
from django.utils.translation import LANGUAGE_SESSION_KEY, gettext_lazy as _
from datetime import datetime
from .functions import getClientIP, FMT_DATE, FMT_TIME, FMT_DATETIME

def absolute_path(req):
    '''
    Get the absolute-path of the application or request
    '''
    RST={}
    url=getattr(settings, 'ABSOLUTE_PATH', None)
    try:
        if not url:
            host=req.build_absolute_uri()
            host=host[0:host.index('/', 9)]
            url=host
        elif url.index('%s')>=0:
            host=req.build_absolute_uri()
            host=host[0:host.index('/', 9)]
            url=url%host
    except ValueError:
        ''' url.index('%s') will raise the ValueError if string not found '''
        pass
    RST['ABSOLUTE_PATH']=url
    RST['now']=datetime.now()
    RST['lang']=req.session.get(LANGUAGE_SESSION_KEY, 'en-US')
    RST['VERSION']=getattr(settings, 'VERSION', 'v0.1.0-beta')
    RST['IPAddr']=getClientIP(req)
    RST['DEBUG']=getattr(settings, 'DEBUG', False)
    RST['METHOD_OVERRIDE']=getattr(settings, 'METHOD_OVERRIDE_PARAM_KEY', '_method')
    if getattr(settings, 'FONTAWESOME_LIC', None): RST['FONTAWESOME_LIC']=getattr(settings, 'FONTAWESOME_LIC', None)
    return RST

def template_injection(req):
    '''
    Inject the TMPL_BASE, TMPL_HEADER, TMPL_FOOTER and TMP_PAGINATION settings into the request
    '''
    lang=getattr(settings, 'LANGUAGE_CODE', 'zh-hant')
    langs=getattr(settings, 'LANGS', ((lang, _(lang)), ))
    RST={
        'TMPL_BLANK': getattr(settings, 'TMPL_BLANK', 'webframe/blank.html'),
        'TMPL_BASE': getattr(settings, 'TMPL_BASE', 'webframe/base.html'),
        'TMPL_HEADER': getattr(settings, 'TMPL_HEADER', 'webframe/header.html'),
        'TMPL_FOOTER': getattr(settings, 'TMPL_FOOTER', 'webframe/footer.html'),
        'TMPL_SCRIPTS': getattr(settings, 'TMPL_SCRIPTS', 'webframe/scripts.html'),
        'TMPL_LOADING': getattr(settings, 'TMPL_SCRIPTS', 'webframe/loading.html'),
        'TMPL_PAGINATION': getattr(settings, 'TMPL_PAGINATION', 'webframe/pagination.html'),
        'URL_LOGIN': getattr(settings, 'URL_LOGIN', '/login/'),
        'URL_LOGOUT': getattr(settings, 'URL_LOGOUT', '/logout/'),
        'LANGS': langs,
    }
    return RST

def fmt_injection(req):
    '''
    Inject the following parameter into request:
      - FMT_DATE: The date-format according to strftime/strptime behavior for date
      - FMT_TIME: The date-format according to strftime/strptime behavior for time
      - FMT_DATETIME: The date-format according to strftime/strptime behavior for date and time
      - FMT_JSDATE: The date-format according to momentjs behavior for date
      - FMT_JSTIME: The date-format according to momentjs behavior for time 
      - FMT_JSDATETIME: The date-format according to momentjs behavior for date and time

    strftime/strptime behavior can be found more here: https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
    momentjs format can be found more here: http://momentjs.com/docs/#/use-it/
    '''
    RST={}
    RST['FMT_DATE']= getattr(settings, 'FMT_DATE', FMT_DATE)
    RST['FMT_TIME']= getattr(settings, 'FMT_TIME', FMT_TIME)
    RST['FMT_DATETIME']= getattr(settings, 'FMT_DATETIME', FMT_DATETIME)

    RST['FMT_JSDATE']= getattr(settings, 'FMT_JSDATE', 'YYYY-MM-DD')
    RST['FMT_JSTIME']= getattr(settings, 'FMT_JSTIME', 'HH:mm:ss')
    RST['FMT_JSDATETIME']= getattr(settings, 'FMT_JSDATETIME', '%s %s'%(RST['FMT_JSDATE'], RST['FMT_JSTIME'])) 

    RST['INDICATOR_MANDATORY']=getattr(settings, 'INDICATOR_MANDATORY', '<span class="mandatory required"><i class="fas fa-shield-alt"></i></span>')
    return RST
