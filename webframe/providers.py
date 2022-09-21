from django.conf import settings
from django.utils.translation import LANGUAGE_SESSION_KEY, gettext_lazy as _
from datetime import datetime
from .functions import getClientIP, FMT_DATE, FMT_TIME, FMT_DATETIME, FMT_TIME_SHORT, FMT_DATETIME_SHORT, convertDateformat 
from .models import Preference, TRUE_VALUES

def getPref(k, v, req, t=30):
   if req is None:
      v=Preference.objects.pref(k, defval=v, returnValue=True)
   else:
      v=Preference.objects.pref(k, defval=v, user=req.user, returnValue=True)
   return v 

def absolute_path(req):
    '''
    Get the absolute-path of the application or request
    '''
    RST={}
    url=getattr(settings, 'ABSOLUTE_PATH', req.build_absolute_uri('/')[:-1])
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
    if hasattr(settings, 'MEDIA_URL'): RST['MEDIA_URL']=getattr(settings, 'MEDIA_URL')
    RST['ABSOLUTE_PATH']=url
    RST['now']=datetime.now()
    RST['lang']=req.session.get(LANGUAGE_SESSION_KEY, 'en-US')
    RST['VERSION']=getattr(settings, 'VERSION', 'v0.1.0-beta')
    RST['IPAddr']=getClientIP(req)
    RST['DEBUG']=getattr(settings, 'DEBUG', False)
    RST['METHOD_OVERRIDE']=getattr(settings, 'METHOD_OVERRIDE_PARAM_KEY', '_method')
    RST['TRUE_VALUES']=TRUE_VALUES
    RST['MEDIA_URL']=getattr(settings, 'MEDIA_URL', '/media')
    if getattr(settings, 'FONTAWESOME_LIC', None): RST['FONTAWESOME_LIC']=getattr(settings, 'FONTAWESOME_LIC', None)
    return RST

def template_injection(req):
    '''
    Inject the TMPL_BASE, TMPL_HEADER, TMPL_FOOTER and TMP_PAGINATION settings into the request
    '''
    lang=getattr(settings, 'LANGUAGE_CODE', 'zh-hant')
    langs=getattr(settings, 'LANGS', ((lang, _(lang)), ))
    RST={
        'TMPL_BASE': getattr(settings, 'TMPL_BASE', 'webframe/base.html'),
        'TMPL_BLANK': getattr(settings, 'TMPL_BLANK', 'webframe/blank.html'),
        'TMPL_FOOTER': getattr(settings, 'TMPL_FOOTER', 'webframe/footer.html'),
        'TMPL_HEADER': getattr(settings, 'TMPL_HEADER', 'webframe/header.html'),
        'TMPL_LOADING': getattr(settings, 'TMPL_SCRIPTS', 'webframe/loading.html'),
        'TMPL_META': getattr(settings, 'TMPL_META', 'webframe/meta.html'),
        'TMPL_MESSAGES': getattr(settings, 'TMPL_MESSAGES', 'webframe/messages.html'),
        'TMPL_PAGINATION': getattr(settings, 'TMPL_PAGINATION', 'webframe/pagination.html'),
        'TMPL_RESET_PASSWORD': getattr(settings, 'TMPL_RESET_PASSWORD', 'webframe/resetPassword.html'),
        'TMPL_SCRIPTS': getattr(settings, 'TMPL_SCRIPTS', 'webframe/scripts.html'),
        'TMPL_STYLE': getattr(settings, 'TMPL_STYLE', None),
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
      - FMT_TIME_SHORT: The date-format according to strftime/strptime behavior for time
      - FMT_DATETIME: The date-format according to strftime/strptime behavior for date and time
      - FMT_DATETIME_SHORT: The date-format according to strftime/strptime behavior for date and time
      - FMT_JSDATE: The date-format according to momentjs behavior for date
      - FMT_JSTIME: The date-format according to momentjs behavior for time 
      - FMT_JSTIME_SHORT: The date-format according to momentjs behavior for time 
      - FMT_JSDATETIME: The date-format according to momentjs behavior for date and time
      - FMT_JSDATETIME_SHORT: The date-format according to momentjs behavior for date and time

    strftime/strptime behavior can be found more here: https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
    momentjs format can be found more here: http://momentjs.com/docs/#/use-it/
    '''
    RST={}
    RST['FMT_DATE']=getPref('FMT_DATE', FMT_DATE, req)
    RST['FMT_TIME']=getPref('FMT_TIME', FMT_TIME, req)
    RST['FMT_TIME_SHORT']=getPref('FMT_TIME_SHORT', FMT_TIME_SHORT, req)
    RST['FMT_DATETIME']=getPref('FMT_DATETIME',  FMT_DATETIME, req)
    RST['FMT_DATETIME_SHORT']=getPref('FMT_DATETIME_SHORT',  FMT_DATETIME_SHORT, req)

    RST['FMT_JSDATE']=convertDateformat(RST['FMT_DATE'], format='javascript')
    RST['FMT_JSTIME']=convertDateformat(RST['FMT_TIME'], format='javascript')
    RST['FMT_JSTIME_SHORT']=convertDateformat(RST['FMT_TIME_SHORT'], format='javascript')
    RST['FMT_JSDATETIME']=convertDateformat(RST['FMT_DATETIME'], format='javascript')
    RST['FMT_JSDATETIME_SHORT']=convertDateformat(RST['FMT_DATETIME_SHORT'], format='javascript')

    RST['INDICATOR_MANDATORY']=getattr(settings, 'INDICATOR_MANDATORY', '<span class="mandatory required indicator-icon"><i class="fas fa-shield-alt"></i></span>')
    return RST
