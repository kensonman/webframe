from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.middleware.csrf import get_token as getCSRF
from django.shortcuts import render, redirect, get_object_or_404 as getObj
from django_tables2 import RequestConfig
from .models import *
from .tables import *

@login_required
def users(req):
	'''
	Show the users page. It is supported to the default User Model (django.contrib.auth.models.User)
	'''
	# Check permission
	if req.user.is_superuser:
		pass
	elif req.user.username==username:
		pass
	elif req.user.has_perms('auth.browse_user'):
		pass
	else:
		return HttpResponseForbidden()

	params=dict()
	params['target']=UserTable(get_user_model().objects.all())
	rc=RequestConfig(req)
	return render(req, 'webframe/users.html', params)

@login_required
def user(req, user):
	user=get_user_model()() if user=='add' else getObj(get_user_model(), username=user)
	params=dict()

	if req.method=='GET':
		# Check permission
		if req.user.is_superuser:
			pass
		elif req.user.username==username:
			pass
		elif req.user.has_perms('auth.browse_user'):
			pass
		else:
			return HttpResponseForbidden()

		# Generate the result
		params['target']=user
		return render(req, 'webframe/user.html', params)
	elif req.method=='DELETE':
		_('User.msg.confirmDelete')
		user.delete()
		return redirect('users')
	elif req.method=='POST':
		# Check permission
		if req.user.is_superuser:
			pass
		elif req.user.username==username:
			pass
		elif user.id is None and req.user.has_perms('auth.add_user'):
			pass
		elif user.id is not None and req.user.has_perms('auth.change_user'):
			pass
		else:
			return HttpResponseForbidden()

		user.first_name=req.POST.get('first_name', None)
		user.last_name=req.POST.get('last_name', None)
		user.email=req.POST.get('email', None)
		if req.user.is_superuser or req.user.has_perms('auth.add_user') or req.user.has_perms('auth.change_user'):
			user.username=req.POST.get('username', None)
			user.is_superuser = req.POST.get('is_superuser', '').upper() in ['TRUE', 'T', 'YES', 'Y', '1']
			user.is_active = req.POST.get('is_active', '').upper() in ['TRUE', 'T', 'YES', 'Y', '1']
			user.is_staff = req.POST.get('is_staff', '').upper() in ['TRUE', 'T', 'YES', 'Y', '1']
		user.save()
		return redirect('users')

@login_required
def prefs(req, user=None):
	'''
	Show the preference page of the specified user. 
	If requesting to show user that is not current session,
	the superuser permission are required.
	'''
	if user==None: user=req.user.username
	if user!=req.user.username and not req.user.is_superuser:
		if req.user.username!=user: return HttpResponseForbidden()
	user=getObj(get_user_model(), username=user)
	params=dict()
	params['preference']=PreferenceTable(Preference.objects.filter(owner=req.user, parent__isnull=True))
	params['config']=PreferenceTable(Preference.objects.filter(owner__isnull=True, parent__isnull=True))
	rc=RequestConfig(req)
	rc.configure(params['preference'])
	rc.configure(params['config'])
	params['currentuser']=user
	return render(req, 'webframe/preferences.html', params)

@login_required
def pref(req, user=None, prefId=None):
	'''
	Showing the preference form for input.
	'''
	# Declare the preference's owner
	if user==None: user=req.user.username
	if user!=req.user.username and not req.user.is_superuser:
		if req.user.username!=user: return HttpResponseForbidden()
	user=getObj(get_user_model(), username=user)

	# Get the target preference
	if prefId=='add':
		pref=Preference()
		pref.isNew=True
		if 'mode' in req.GET and req.GET.get('mode', None)==getCSRF(req):
			pref.user=None
		else:
			pref.user=user
		if 'parent' in req.GET: pref.parent=getObj(Preference, id=req.GET['parent'])
	else:
		pref=getObj(Preference, id=prefId)
	
	if req.method=='GET':
		# Preparing the form view
		params=dict()
		params['target']=pref
		params['childs']=PreferenceTable(pref.childs())
		params['currentuser']=user
		return render(req, 'webframe/preference.html', params)
	elif req.method=='POST':
		# Saving
		if req.user.is_superuser:
			pass #Allow superuser
		elif pref.isNew() and req.user.has_perms('webframe.add_preference'):
			pass #Allow to add preference
		elif (not pref.isNew()) and req.user.has_perms('webframe.change_preference'):
			pass #Allow to change preference
		else:
			return HttpResponseForbidden()

		pref.name=req.POST['name']
		pref.value=req.POST['value']
		pref.sequence=int(req.POST['sequence'])
		pref.parent=None if req.POST.get('parent') is None else getObj(Preference, id=req.POST['parent'])
		pref.owner=user
		pref.save()
	elif req.method=='DELETE':
		# Delete the method
		_('Preference.msg.confirmDelete')
		pref.delete()
	if pref.parent:
		return redirect('preference', user=user.username, prefId=pref.parent.id)
	else:
		return redirect('preferences', user=user.username)
		
