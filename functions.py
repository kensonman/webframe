#-*- coding: utf-8 -*-

def getClientIP( req ):
	'''
	Get the client ip address

	@param req The request;
	'''
	xForwardedFor=req.META.get('HTTP_X_FORWARDED_FOR')
	if xForwardedFor:
		ip=xForwardedFor.split(',')[0]
	else:
		ip=req.META.get('REMOTE_ADDR')
	return ip

def getBool( val, defVal=False, trueOpts=['YES', 'Y', '1', 'TRUE', 'T'] ):
	'''
	Retrieve the boolean value from string

	@param val The value to be parse to bool
	@param defVal The default value if the val is None
	@param trueOpts The available values of TRUE
	'''
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
	
