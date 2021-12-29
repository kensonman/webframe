from django import template
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.utils.functional import SimpleLazyObject
from django.utils.safestring import SafeString
from webframe.models import Preference
from webframe.functions import valueOf, TRUE_VALUES
from webframe.CurrentUserMiddleware import get_current_user
import logging

logger=logging.getLogger('webframe.templatetags')

register=template.Library()

@register.simple_tag(takes_context=True)
def pref(context, prefName, **kwargs):
   '''
   Retrieve the preference from the database.

   Usage: 
      1. Import the template-tag by: {%load pref%}
      2. Access the preference with parameter(s): {%pref 'prefName' defval='Default Value' as pref%};

      All the parameters can be references webframe.models.PrefManager.pref

         @param defval      The default value. If the preference/config not found, return the default value instead;
         @param user        The owner of this preference. If you would like to access the config, setup this parameter to None;
         @param returnValue It will told the template-tag to return the preference's value instead of the preference instead; DEFAULT True
         @param markSafe    When returnValue is True, indicate the value should be mark-safe; Default False
         @param lang        Using the lang parameter when loading preference (refer to Preference.objects.pref(name, **kwargs) for more details
   '''
   try:
      if 'user' in kwargs:
         user=kwargs['user']
         if user is None:
            del kwargs['user']
         else:
            if isinstance(user, AnonymousUser):
               del kwargs['user']
            elif hasattr(user, 'is_anonymous') and valueOf(user.is_anonymous):
               del kwargs['user']
            elif not isinstance(user, User):
               kwargs['user']=User.objects.get(username=str(kwargs['user']))
      else:
         kwargs['user']=get_current_user()
      if 'lang' not in kwargs:
         lang=context.request.headers.get('Accept-Language', '*')
         if lang!='*':
            lang='{0},en;q=0.0001'.format(lang)
            kwargs['lang']=lang
      pref=Preference.objects.pref(prefName, **kwargs)
      logger.debug('pref[{0}]=={1}'.format(prefName, pref))
      if kwargs.get('returnValue', 'True') in TRUE_VALUES:
         if kwargs.get('markSafe', 'False') in TRUE_VALUES:
            pref=SafeString(pref)
      return pref
   except Preference.DoesNotExist:
      return "{Pref<%s> Not Found}"%prefName
   
@register.filter
def boolean(value):
   '''
   Cast the value into bool
   '''
   if not value: return False
   return value in TRUE_VALUES

@register.simple_tag(takes_context=True)
def conf(context, confName, **kwargs):
   '''
   Retrieve the settings information.

   Usage:
      1. Import the template-tag by: {%load pref%}
      2.  Access the settings with parameter(s): {%conf 'DEBUG' as DebugInSettings%};
   '''
   defval=kwargs.get('defval', '{{conf[{0}] not found}}'.format(confName))
   try:
      if not hasattr(settings, confName):  raise ValueError('hasattr(settings, \"{0}\") not found.')
      return getattr(settings, confName, defval)
   except ValueError as ex:
      logger.debug(ex)
      return defval
