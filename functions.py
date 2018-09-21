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

def getBool( val, defVal=False, trueOpts=['YES', 'Y', '1', 'TRUE', 'T', 'ON'] ):
   '''
   Retrieve the boolean value from string

   @param val The value to be parse to bool
   @param defVal The default value if the val is None
   @param trueOpts The available values of TRUE
   '''
   if callable(val): val=val()
   if val:
      return str(val).upper() in trueOpts
   return defVal 

def getDate( val, defVal=None, fmt=FMT_DATE ):
   '''
   Retrieve the date from string.

   @param val The value to be parse to bool
   @param defVal The default value if the val is None
   @param fmt The specified format according to Python: datetime.strptime
   '''
   return getTime(val, defVal=defVal, fmt=fmt)

def getTime( val, defVal=None, fmt=FMT_TIME ):
   '''
   Retrieve the time from string.

   @param val The value to be parse to bool
   @param defVal The default value if the val is None
   @param fmt The specified format according to Python: datetime.strptime
   '''
   if not val: return defVal
   if isinstance(val, datetime): return val
   try:
      rst=datetime.strptime(val, fmt)
      return timezone.make_aware(rst)
   except ValueError:
      return defVal

def getDateTime( val, defVal=None, fmt=FMT_DATETIME ):
   '''
   Retrieve the datetime from string.

   @param val The value to be parse to bool
   @param defVal The default value if the val is None
   @param fmt The specified format according to Python: datetime.strptime
   '''
   return getTime(val, defVal=defVal, fmt=fmt)

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
