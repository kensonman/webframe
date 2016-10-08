from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404 as getObj
from django.contrib.auth.decorators import login_required
from webframe.models import *

@login_required
def prefs(req, user=None):
	'''
	Show the preference page of the specified user. 
	If requesting to show user that is not current session,
	the superuser permission are required.
	'''
	if user==None: user=req.user.username
	if not req.user.is_superuser:
		if req.user.username!=user: return HttpResponseForbidden()
	params=dict()
	params['target']=Preference.objects.filter(user=req.user)
	params['general']=Preference.objects.filter(user__isnull=True)
	return render(req, 'webframe/preferences.html', params)

@login_required
def pref(req, user=None, prefId=None):
	if prefId=='add':
		pref=Preference()
	else:
		pref=getObj(Preference, id=prefId)
	params=dict()
	params['target']=pref
	return render(req, 'webframe/preference.html', params)
