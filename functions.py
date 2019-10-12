#-*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.conf import settings
from django.http import HttpRequest
from django.utils import timezone
from netaddr import IPAddress, IPNetwork
from deprecation import deprecated
import os, logging, pytz

logger=logging.getLogger('webframe.functions')
FMT_DATE=getattr(settings, 'FMT_DATE', '%Y-%m-%d')
FMT_TIME=getattr(settings, 'FMT_TIME', '%H:%M:%S')
FMT_DATETIME=getattr(settings, 'FMT_DATETIME', '%s %s'%(FMT_DATE, FMT_TIME))
 
def valueOf(obj, defval=None):
   '''
   Get the value of the specified object, if it is callable/method/function, execute it and return the result;
   '''
   if obj==None: return defval 
   if hasattr(obj, 'valueOf'): obj=obj.valueOf()
   if hasattr(obj, '__call__'): obj=obj()
   if isinstance(obj, str):
      obj=obj.strip()
      if len(obj)<1: return defval 
   return obj

def getClass( cls ):
   '''
   Get the class from a string.
   '''
   parts=cls.split('.')
   m=__import__('.'.join(parts[:-1]))
   for c in parts[1:]:
      m=getattr(m, c)
   return m

def getClientIP( req ):
   '''
   Get the client ip address

   @param req The request;
   '''
   if callable(req): req=req()
   xForwardedFor=req.META.get('HTTP_X_FORWARDED_FOR')
   if xForwardedFor:
      ip=xForwardedFor.split(',')[0]
   else:
      ip=req.META.get('REMOTE_ADDR')
   return ip

def inNetworks( ipaddr, networks=['192.168.0.0/255.255.255.0',]):
    '''
    Returns TRUE if the specified IP address is belongs to one of the specified networks.

    @param ipaddr The instance of netaddr.IPAddress or an instance of HttpRequest;
    @param networks An array of the acceptant networks (e.g.: '192.168.0.0/255.255.255.0' or '192.168.1.0/24');
    '''
    if callable(ipaddr): ipaddr=ipaddr()
    if isinstance(ipaddr, HttpRequest):
        ipaddr=IPAddress(getClientIP(ipaddr))
    for network in networks:
        if not isinstance(network, IPNetwork):
            '''Cast the network into IPNetwork instance'''
            network=IPNetwork(str(network))

        if ipaddr in network:
            return True
    return False

def getBool( val, defval=False, trueOpts=['YES', 'Y', '1', 'TRUE', 'T', 'ON'] ):
   '''
   Retrieve the boolean value from string

   @param val The value to be parse to bool
   @param defval The default value if the val is None
   @param trueOpts The available values of TRUE
   '''
   if callable(val): val=val()
   if val:
      return str(val).upper() in trueOpts
   return defval 

def getDate( val, **kwargs ):
   '''
   Retrieve the date from string.

   @param val        The value to be parse to bool;
   @param defval     The default value if the val is None;
   @param fmt        The specified format according to Python: datetime.strptime;
   @param daystart   The indicator to get the begining of the day;
   @param dayend     The indicator to get the end of the day;
   '''
   if not 'fmt' in kwargs or kwargs['fmt']==None: kwargss['fmt']=FMT_DATE
   return getTime(val, **kwargs)

def getTime( val, **kwargs ):
   '''
   Retrieve the time from string.

   @param val        The value to be parse to bool;
   @param defval     The default value if the val is None;
   @param fmt        The specified format according to Python: datetime.strptime;
   @param daystart   The indicator to get the begining of the day;
   @param dayend     The indicator to get the end of the day;
   '''
   if not val: return kwargs.get('defval', None) 
   if isinstance(val, datetime): return val
   fmt=kwargs.get('fmt', FMT_TIME)
   try:
      rst=datetime.strptime(val, fmt)
      rst=timezone.make_aware(rst)
      if 'daystart' in kwargs: rst=rst.replace(hour=0, minute=0, second=0, microsecond=0)
      if 'dayend' in kwargs:   rst=rst.replace(hour=23, minute=59, second=59, microsecond=999999)
      return rst
   except ValueError:
      return kwargs.get('defval', None) 

def getDateTime( val, **kwargs ):
   '''
   Retrieve the datetime from string.

   @param val        The value to be parse to bool;
   @param defval     The default value if the val is None;
   @param fmt        The specified format according to Python: datetime.strptime;
   @param daystart   The indicator to get the begining of the day;
   @param dayend     The indicator to get the end of the day;
   '''
   if not 'fmt' in kwargs or kwargs['fmt']==None: kwargss['fmt']=FMT_DATETIME
   return getTime(val, **kwargs)

def checkRecaptcha( req, secret, simple=True ):
   '''
   Checking the recaptcha and return the result.

   @param req The request;
   @param secret The secret retreived from Google reCaptcha registration;
   @param simple Retrue the simple boolean value of verification if True, otherwise, return the JSON value of verification;
   '''
   import requests
   apiurl='https://www.google.com/recaptcha/api/siteverify'
   fieldname='g-recaptcha-response'

   answer=req.POST.get(fieldname, None)
   clientIP=getClientIP( req )
   rst=requests.post(apiurl, data={'secret': secret, 'response':answer, 'remoteip': clientIP}).json()
   if simple:
      return getBool(rst.get('success', 'False'))
   return r.json()

def getEndOfDay(date):
   '''
   Get the end of the date.

   e.g.: getEndOfDay('2017-09-03') => '2017-09-03 23:59:59.999'
   '''
   rst=date+timedelta(days=1)
   return rst-timedelta(milliseconds=1)

def link_callback(uri, rel):
   '''
   Translate the link to the local resources (Used for PDF generating).
   '''
   # use short variable names
   sUrl = settings.STATIC_URL      # Typically /static/
   sRoot = settings.STATIC_ROOT   # Typically /home/userX/project_static/
   mUrl = settings.MEDIA_URL       # Typically /static/media/
   mRoot = settings.MEDIA_ROOT     # Typically /home/userX/project_static/media/

   # convert URIs to absolute system paths
   if uri.startswith(mUrl):
      path = os.path.join(os.getcwd(), mRoot, uri.replace(mUrl, ""))
   elif uri.startswith(sUrl):
      path = os.path.join(os.getcwd(), sRoot, uri.replace(sUrl, ""))
   else:
      path=uri

   # make sure that file exists
   if not os.path.isfile(path):
      raise Exception('media URI must start with %s or %s, but %s' % (sUrl, mUrl, path))
   logger.debug('Translate URL: %s => %s'%(uri, path))
   return path

def getChoice(choices, val):
   '''
   Translate the choices.

   e.g.:
   Giving EXAMPLE=( (0, 'zero'), (1, 'one'), (4, 'two'), (3, 'three'), )
      - getChoices(EXAMPLE, 0) => 'zero'
      - getChoices(EXAMPLE, 3) => 'three'
      - getChoices(EXAMPLE, 'one') => 1 (Index of 'one' element)
      - getChoices(EXAMPLE, 'two') => 4 (Index of 'two' element)
   '''
   if isinstance(val, int) or val.isdigit():
      val=int(val)
      return choices[val][1]
   else:
      val=str(val).upper()
      cnt=0
      for s in choices:
         if s[1].upper()==val:
            return cnt
         cnt+=1
      return -1

@deprecated(deprecated_in='1.0', removed_in='2.0', details='Use getChoice(choices, val) instead')
def getChoices(choices, val):
   '''
   Alias of getChoice(choices, val) for backward compatible
   '''
   return getChoice(choices, val)

def convertDateformat(pydateformat, format='javascript'):
   '''
   Convert the Python's date-format into Javascript format
   @param pydateformat                    The date-format to be converted
   @param format                          The style required. Currently support: javascript, java
   '''
   if format=='javascript':
      keys={
         '%A': 'dddd',                       #Weekday as locale’s full name: (In English: Sunday, .., Saturday)(Auf Deutsch: Sonntag, .., Samstag)   
         '%a': 'ddd',                        #Weekday abbreivated: (In English: Sun, .., Sat)(Auf Deutsch: So, .., Sa)
         '%B': 'MMMM',                       #Month name: (In English: January, .., December)(Auf Deutsch: Januar, .., Dezember)
         '%b': 'MMM',                        #Month name abbreviated: (In English: Jan, .., Dec)(Auf Deutsch: Jan, .., Dez)
         '%c': 'ddd MMM DD HH:mm:ss YYYY',   #Locale’s appropriate date and time representation: (English: Sun Oct 13 23:30:00 1996)(Deutsch: So 13 Oct 22:30:00 1996) 
         '%d': 'DD',                         #Day 0 padded: (01, .., 31)
         '%f': 'SSS',                        #Microseconds 0 padded: (000000, .., 999999)
         '%H': 'HH',                         #Hour (24-Hour) 0 padded: (00, .., 23) 
         '%I': 'hh',                         #Hour (12-Hour) 0 padded: (01, .., 12)
         '%j': 'DDDD',                       #Day of Year 0 padded: (001, .., 366) 
         '%M': 'mm',                         #Minute 0 padded: (01, .. 59) 
         '%m': 'MM',                         #Month 0 padded: (01, .., 12)
         '%p': 'A',                          #Locale equivalent of AM/PM: (EN: AM, PM)(DE: am, pm)
         '%S': 'ss',                         #Second 0 padded: (00, .., 59)
         '%U': 'ww',                         #Week # of Year (Sunday): (00, .., 53)  All days in a new year preceding the first Sunday are considered to be in week 0.
         '%W': 'ww',                         #Week # of Year (Monday): (00, .., 53)  All days in a new year preceding the first Monday are considered to be in week 0.
         '%w': 'd',                          #Weekday as #: (0, 6)
         '%X': 'HH:mm:ss',                   #Locale's appropriate time representation: (EN: 23:30:00)(DE: 23:30:00)
         '%x': 'MM/DD/YYYY',                 #Locale's appropriate date representation: (None: 02/14/16)(EN: 02/14/16)(DE: 14.02.16)
         '%Y': 'YYYY',                       #Year as #: (1970, 2000, 2038, 292,277,026,596)
         '%y': 'YY',                         #Year without century 0 padded: (00, .., 99)
         '%Z': 'z',                          #Time zone name: ((empty), UTC, EST, CST) (empty string if the object is naive).
         '%z': 'ZZ',                         #UTC offset in the form +HHMM or -HHMM: ((empty), +0000, -0400, +1030) Empty string if the the object is naive.
         '%%': '%',                          #A literal '%' character: (%)
      }
   elif format=='java':
      keys={
         '%A': 'EEEE',                       #Weekday as locale’s full name: (In English: Sunday, .., Saturday)(Auf Deutsch: Sonntag, .., Samstag)   
         '%a': 'E',                          #Weekday abbreivated: (In English: Sun, .., Sat)(Auf Deutsch: So, .., Sa)
         '%B': 'MMMM',                       #Month name: (In English: January, .., December)(Auf Deutsch: Januar, .., Dezember)
         '%b': 'MMM',                        #Month name abbreviated: (In English: Jan, .., Dec)(Auf Deutsch: Jan, .., Dez)
         '%c': 'ddd MMM DD HH:mm:ss YYYY',   #Locale’s appropriate date and time representation: (English: Sun Oct 13 23:30:00 1996)(Deutsch: So 13 Oct 22:30:00 1996) 
         '%d': 'dd',                         #Day 0 padded: (01, .., 31)
         '%f': 'SSSS',                       #Microseconds 0 padded: (000000, .., 999999)
         '%H': 'HH',                         #Hour (24-Hour) 0 padded: (00, .., 23) 
         '%I': 'hh',                         #Hour (12-Hour) 0 padded: (01, .., 12)
         '%j': 'DDD',                        #Day of Year 0 padded: (001, .., 366) 
         '%M': 'mm',                         #Minute 0 padded: (01, .. 59) 
         '%m': 'MM',                         #Month 0 padded: (01, .., 12)
         '%p': 'A',                          #Locale equivalent of AM/PM: (EN: AM, PM)(DE: am, pm)
         '%S': 'ss',                         #Second 0 padded: (00, .., 59)
         '%U': 'ww',                         #Week # of Year (Sunday): (00, .., 53)  All days in a new year preceding the first Sunday are considered to be in week 0.
         '%W': 'ww',                         #Week # of Year (Monday): (00, .., 53)  All days in a new year preceding the first Monday are considered to be in week 0.
         '%w': 'd',                          #Weekday as #: (0, 6)
         '%X': 'HH:mm:ss',                   #Locale's appropriate time representation: (EN: 23:30:00)(DE: 23:30:00)
         '%x': 'MM/dd/yyyy',                 #Locale's appropriate date representation: (None: 02/14/16)(EN: 02/14/16)(DE: 14.02.16)
         '%Y': 'yyyy',                       #Year as #: (1970, 2000, 2038, 292,277,026,596)
         '%y': 'yy',                         #Year without century 0 padded: (00, .., 99)
         '%Z': 'z',                          #Time zone name: ((empty), UTC, EST, CST) (empty string if the object is naive).
         '%z': 'ZZ',                         #UTC offset in the form +HHMM or -HHMM: ((empty), +0000, -0400, +1030) Empty string if the the object is naive.
         '%%': '%',                          #A literal '%' character: (%)
      }


   result=pydateformat
   for k in keys:
      result=result.replace(k, keys[k])
   return result

@deprecated(deprecated_in='1.0', removed_in='2.0', details='Use convertDateformat(pydateformat, format="javascript") instead')
def getJSDateformat(pydateformat, format='javascript'):
   return convertDateformat(pydateformat, format)

