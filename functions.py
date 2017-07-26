#-*- coding: utf-8 -*-
from django.http import HttpRequest
from netaddr import IPAddress, IPNetwork

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
