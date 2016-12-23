from django import template
from django.contrib.auth.models import User
from webframe.models import Preference
from webframe.CurrentUserMiddleware import get_current_user

register=template.Library()

@register.assignment_tag
def pref(prefName, **kwargs):
	'''
	Retrieve the preference from the database.

	Usage: 
		1. Import the template-tag by: {%load pref%}
		2. Access the preference with parameter(s): {%pref 'prefName' defval='Default Value' as pref%};

		All the parameters can be references webframe.models.PrefManager.pref

			@param defval The default value. If the preference/config not found, return the default value instead;
			@param user The owner of this preference. If you would like to access the config, setup this parameter to None;
			@param returnValue The template-tag parameter. It will told the template-tag to return the preference's value instead of the preference instead;

	'''
	try:
		if 'user' in kwargs:
			if kwargs['user'] is None:
				del kwargs['user']
			elif not isinstance(kwargs['user'], User):
				kwargs['user']=User.objects.get(username=kwargs['user'])
		else:
			kwargs['user']=get_current_user()
		pref=Preference.objects.pref(prefName, **kwargs)
		if str(kwargs.get('returnValue', 'False')).upper() in ['TRUE', 'T', 'YES', 'Y', '1']:
			return pref.value
		return pref
	except Preference.DoesNotExist:
		return "{Pref<%s> Not Found}"
	
@register.filter
def boolean(value):
	'''
	Cast the value into bool
	'''
	if not value: return False
	return str(value).upper() in ['TRUE', 'T', 'YES', 'Y', '1']
