#-*- coding: utf-8 -*-

def getClientIP( req ):
	'''
	Get the client ip address
	'''
	xForwardedFor=req.META.get('HTTP_X_FORWARDED_FOR')
	if xForwardedFor:
		ip=xForwardedFor.split(',')[0]
	else:
		ip=req.META.get('REMOTE_ADDR')
	return ip

def getBool( val, trueOpts=['YES', 'Y', '1', 'TRUE', 'T'] ):
	'''
	Retrieve the boolean value from string
	'''
	if val:
		return str(val).upper() in trueOpts
	return False
