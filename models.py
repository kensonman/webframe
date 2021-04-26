# -*- coding: utf-8 -*-
# File:     webframe/models.py
# Author:   Kenson Man <kenson@kensonidv.hk>
# Date:     2020-10-17 12:29
# Desc:     Provide the basic model for webframe
from datetime import datetime
from deprecation import deprecated
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404 as getObj
from django.utils import timezone as tz
from django.utils.translation import ugettext_lazy as _
from json import JSONEncoder
from pathlib import Path
from shutil import copyfile
from .CurrentUserMiddleware import get_current_user
from .functions import getBool, getClass, getTime, FMT_DATE, FMT_TIME, FMT_DATETIME, isUUID, TRUE_VALUES, getSecretKey, encrypt, decrypt, ENCRYPTED_PREFIX, LogMessage as lm, cache
import math, uuid, logging, json, pytz, re, sys, os

logger=logging.getLogger('webframe.models')

DATEFMT='%Y-%m-%d %H:%M:%S.%fT%z'
fmt=lambda d: 'null' if d is None else d.strftime(DATEFMT)
rfmt=lambda d: None if d=='null' else datetime.strptime(d, DATEFMT)
nullValue=_('null') #Make sure the null value can be translate
#Make sure the following transaction
_('Traditional Chinese')
_('English')

def valueOf(val):
   '''
   Parse the value into string format
   '''
   if isinstance(val, datetime):
     rst=fmt(val)
   elif isinstance(val, get_user_model()):
     rst=val.username
   elif isinstance(val, uuid.UUID):
     rst=val.hex
   elif isinstance(val, ValueObject):
     rst=val.id.hex
   else:
     rst=val
   return rst

def parseVal(field, val):
   '''
   Parse the value from dumpable format
   '''
   typ=field.get_internal_type()
   if val is None:
     return None
   elif typ in ['AutoField', 'IntegerField', 'SmallIntegerField']:
     return int(val)
   elif typ in ['BigAutoField', 'BigIntegerField']:
     return long(val)
   elif typ in ['FloatField', 'DecimalField']:
     return float(val)
   elif typ == 'BooleanField':
     return getBool(val)
   elif typ in ['UUIDField']:
     return uuid.UUID(val)
   elif typ in ['CharField', 'TextField', 'EmailField', 'URLField']:
     return str(val)
   elif typ == 'DateTimeField':
     return datetime.strptime(val, DATEFMT)
   elif typ == 'ForeignKey':
     if field.related_model is get_user_model():
       try:
         return get_user_model().objects.get(username=val)
       except get_user_model().DoesNotExist:
         rst=get_current_user()
         logger.warning('Specify user<%s> not found, use current user<%s> instead.'%(val, rst))
         return rst
     return getObj(field.related_model, id=val)
   return str(val)

class ValueEncoder(JSONEncoder):
   def default(self, o):
     if isinstance(o, uuid.UUID):
       return o.hex
     return super(ValueEncoder, self).default(o)

class Dictable(object):
   '''
   The class to provide the import/export json method.
   '''

   META_TYPE='_type_'
   META_VERS='_vers_'

   def expDict(self, **kwargs):
     '''
     The method to export dictionary. It will ignore the properties that:
      - prefix with "_"
      - subfix with "_id"
     '''
     src=self.__dict__
     rst=dict()
     for k in src:
       if k.startswith('_'): continue
       if k.endswith('_id'): continue
       rst[k]=src[k]
     rst[Dictable.META_TYPE]="%s.%s"%(self.__class__.__module__, self.__class__.__name__)
     rst[Dictable.META_VERS]=self._getDictVers()
     for f in self.__class__._meta.get_fields():
       if isinstance(f, models.Field):
         n=f.name
         v=getattr(self, n)
         rst[n]=valueOf(v)
     return rst

   def impDict(self, data, **kwargs):
     '''
     The method to import from dictionary.
     '''
     if not Dictable.META_TYPE in data: raise TypeError('This is not the dictionary created by expDict. No type information found')
     if not isinstance(self, getClass(data[Dictable.META_TYPE])): raise TypeError('Cannot import %s as %s'%(data[Dictable.META_TYPE], self.__class__))
     if hasattr(self, Dictable.META_VERS):
       if self._getDictVers() != data[Dictable.META_VERS]: raise IOError('Version mismatched. Requesting %s but %s'%(getattr(self, Dictable.META_VERS), data[Dictable.META_VERS]))

     for f in self.__class__._meta.get_fields():
       if isinstance(f, models.Field):
         n=f.name
         v=parseVal(f, data.get(n, None))
         setattr(self, n, v)
     if getBool(kwargs.get('createNew', 'false')): self.id=None
     if getBool(kwargs.get('autoSave', 'false')): self.save()
     return self

   def _getDictVers(self):
     '''
     Getter of the dictionary version. It is used to limit the version of dict.
     '''
     return getattr(self, Dictable.META_VERS, '1')

   @staticmethod
   def getType( instance ):
      mod=instance.__class__.__module__
      if mod is None or mod==str.__class__.__module__:
         return instance.__class__.__name__
      else:
         return '{0}.{1}'.format(mod, instance.__class__.__name__)

class ValueObject(models.Model, Dictable):
   CACHED='__CACHED__'

   class Meta(object):
     abstract      = True
     verbose_name      = _('webframe.models.ValueObject')
     verbose_name_plural = _('webframe.models.ValueObjects')
     # view_* permission becomes the default permissions Django 3.0

   id              = models.UUIDField(
     primary_key=True,
     default=uuid.uuid4,
     editable=False,
     verbose_name=_('webframe.models.ValueObject.id'),
     help_text=_('webframe.models.ValueObject.id.helptext'),
   )
   lmd             = models.DateTimeField(
     auto_now=True,
     verbose_name=_('webframe.models.ValueObject.lmd'),
     help_text=_('webframe.models.ValueObject.lmd.helptext'),
   )
   lmb             = models.ForeignKey(
     settings.AUTH_USER_MODEL,
     default=get_current_user,
     null=True,
     blank=True,
     on_delete=models.CASCADE, #Since Django 2.0, the on_delete field is required.
     related_name='%(class)s_lmb',
     verbose_name=_('webframe.models.ValueObject.lmb'),
     help_text=_('webframe.models.ValueObject.lmb.helptext'),
   )
   cd              = models.DateTimeField(
     auto_now_add=True,
     verbose_name=_('webframe.models.ValueObject.cd'),
     help_text=_('webframe.models.ValueObject.cd.helptext'),
   )
   cb              = models.ForeignKey(
     settings.AUTH_USER_MODEL,
     default=get_current_user,
     null=True,
     blank=True,
     on_delete=models.CASCADE, #Since Django 2.0, the on_delete field is required.
     related_name='%(class)s_cb',
     verbose_name=_('webframe.models.ValueObject.cb'),
     help_text=_('webframe.models.ValueObject.cb.helptext'),
   )

   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      if 'id' in kwargs: self.id=kwargs['id']
      if 'cb' in kwargs: self.cb=kwargs['cb']
      if 'cd' in kwargs: self.cd=kwargs['cd']
      if 'lmb' in kwargs: self.lmb=kwargs['lmb']
      if 'lmd' in kwargs: self.lmd=kwargs['lmd']

   @property
   def isNew(self):
      return self.lmd is None

   @property
   def isNotNew(self):
      return self.lmd is not None

   def id_or_new(self):
      if self.isNew():
         return 'new'
      return self.id.hex

   def save(self, *args, **kwargs):
      '''
      Saving the value-object. The method will setup the lmb default value
      '''
      user=get_current_user()
      if user:
         if not user.is_authenticated: user=None
      if kwargs.get('update_lmb', 'true') in TRUE_VALUES:
         self.lmb=user
      if kwargs.get('update_cb', 'true') in TRUE_VALUES:
         try:
            if not self.cb: self.cb=user
         except TypeError:
            self.cb=user
      super(ValueObject, self).save()
   
   def expDict(self):

      return {
           Dictable.META_VERS:    1
         , Dictable.META_TYPE:    Dictable.getType(self)
         , 'id':        self.id
         , 'cb':        {Dictable.META_TYPE: Dictable.getType(self.cb), 'id': self.cb.id, 'username': self.cb.username, 'email': self.cb.email} if self.cb else None
         , 'cd':        self.cd
         , 'lmb':       {Dictable.META_TYPE: Dictable.getType(self.lmb), 'id': self.lmb.id, 'username': self.lmb.username, 'email': self.lmb.email} if self.lmb else None
         , 'lmd':       self.lmd
      }

class AliveObjectManager(models.Manager):
   def living(self, timestamp=None):
      '''
      The alias of alive for backward compatibility.
      '''
      return self.alive(timestamp)

   def alive(self, timestamp=None):
      '''
      Return the alive objects according to the specified timestamp.
      '''
      now=tz.now() if timestamp is None else timestamp
      return self.filter(enabled=True,effDate__lte=now).filter(models.Q(expDate__isnull=True)|models.Q(expDate__gt=now)).order_by('-effDate')

   def dead(self, timestamp=None):
      '''
      Return the dead objects according to the specified timestamp.
      '''
      now=tz.now() if timestamp is None else timestamp
      return self.filter(
         models.Q(enabled=False)|
         models.Q(effDate__gt=now)|
         (
            models.Q(expDate__isnull=False)&
            models.Q(expDate__lt=now)
         )
      ).order_by('-effDate')

   @deprecated(deprecated_in="v2.2", removed_in="v3.0", current_version="v2.2", details="Use AliveObject.isOverlapped(start, end) instead")
   def isOverlaped(self, start, end):
      '''
      Determinate the specified period is overlaped with the object effective period.
      '''
      return self.isOverlapped(start, end)

   def isOverlapped(self, start, end):
      '''
      Determinate the specified period is overlaped with the object effective period.
      
      Giving:
        - source beging date == self.effDate
        - source end date    == self.expDate
        - target beging date == start
        - target end date    == end
      Refer to https://stackoverflow.com/questions/14002907/query-to-get-date-overlaping, the defination of overlaping is
          ***** NOT (taget_end_date < source_begin_date or target_begin_date > source_end_date ) *****
      That is equal than:
         not (target_end_date < source_beging_date) and not (target_beging_date > source_end_date)
      Therefore:
         (effDate__lte=end, expDate__gte=start)
      '''
      return self.filter(effDate__lte=end, expDate__gte=start)

class AliveObject(models.Model, Dictable):
   class Meta(object):
      abstract         = True
      verbose_name      = _('webframe.models.AliveObject')
      verbose_name_plural = _('webframe.models.AliveObjects')

   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      if 'effDate' in kwargs: self.effDate=kwargs['effDate']
      if 'expDate' in kwargs: self.expDate=kwargs['expDate']
      if 'enabled' in kwargs: self.enabled=kwargs['enabled']
   
   effDate             = models.DateTimeField(
                     default=tz.now,
                     verbose_name=_('webframe.models.AliveObject.effDate'),
                     help_text=_('webframe.models.AliveObject.effDate.helptext'),
                  )
   expDate             = models.DateTimeField(
                     null=True,
                     blank=True,
                     verbose_name=_('webframe.models.AliveObject.expDate'),
                     help_text=_('webframe.models.AliveObject.expDate.helptext'),
                  )
   enabled             = models.BooleanField(
                     default=True,
                     verbose_name=_('webframe.models.AliveObject.enabled'),
                     help_text=_('webframe.models.AliveObject.enabled.helptext'),
                  )
   objects             = AliveObjectManager()

   def isNew(self):
      '''
      Determinate the object is just create (haven't saved).
      '''
      return self.lmd is None

   def isNotNew(self):
      '''
      Determinate the object is create create (haven't saved).
      '''
      return not self.lmd is None

   def isEffective(self, now=None):
      '''
      Deprecated. Use isAlive(now=None) instead.
      '''
      return self.isAlive(now)

   def isAlive(self, now=None):
      '''
      Determinate the objct is alive (is-effective).
      '''
      if not now: now=tz.now()
      return self.enabled and self.effDate<=now and (self.expDate is None or self.expDate>now)

   def isDead(self, now=None):
      '''
      Determinate the objct was dead (is-not-effective).
      '''
      return not self.isAlive(now)

   def asDict(self):
      return {'effDate':fmt(self.effDate), 'expDate':fmt(self.expDate), 'enabled':self.enabled}

   def fromDict(self, data):
      self.effDate=rfmt(data['effDate'])
      self.expDate=rfmt(data['expDate'])
      self.enabled=getBool(data['enabled'])

   @property
   def alive(self):
      return self.isAlive()

# The abstract value=object that provide the sequence field and related ordering features
class OrderableValueObject(ValueObject):
   DISABLED_REORDER = 'DISABLED_REORDER'
   sequence      = models.FloatField(default=sys.maxsize,verbose_name=_('webframe.models.OrderableValueObject.sequence'))

   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      if 'sequence' in kwargs: self.sequence=kwargs['sequence']

   class Meta:
      abstract   = True
      ordering   = ['sequence', 'id',]

   # Get the ordering features
   def __get_ordered_list__(self):
      '''
      Get the ordered list. Returns None to disable the re-ordering feature when saving
      '''
      if hasattr(self.__class__, OrderableValueObject.DISABLED_REORDER) or hasattr(settings, OrderableValueObject.DISABLED_REORDER): return None
      return self.__class__.objects.all().order_by('sequence')

   # Saving and reorder the models
   def save(self, *args, **kwargs):
      if getBool(getattr(self.__class__, OrderableValueObject.DISABLED_REORDER, 'False')) or getBool(getattr(kwargs, OrderableValueObject.DISABLED_REORDER,'False')):
         super().save(*args, **kwargs)
      else:
         self.sequence-=0.5
         super().save(*args, **kwargs)
         reordered=self.__get_ordered_list__() #Retrieve the list again due to the sequence changed
         cnt=1
         if reordered: 
            for i in reordered:
               self.__class__.objects.filter(id=i.id).update(sequence=cnt)
               cnt+=1

   def expDict(self):
      rst=super().expDict()
      rst['sequence']=self.sequence
      return rst

class PrefManager(models.Manager):
   def pref(self, name=None, **kwargs):
     '''
     Get the preference from database.
     
     @name                   The filter of preference name or UUID
     @kwargs['defval']       The filter of default value
     @kwargs['owner']        The filter of preference owner
     @kwargs['user']         The alias of "owner"
     @kwargs['config']       Default False; The boolean value indicate the method should allow None owner as the result; (return the first occurence);
     @kwargs['returnValue']  Default True;  The boolean value indicate the method return the preference's value instead of preference instance.
     @kwargs['returnQuery']  Default False; The boolean value indicate the method return the query instead of others; [for debug];
     @kwargs['parent']       The filter of parent preference of result instance
     @kwargs['value']        The filter of preference value; the below operators can be used:
                                 == The equals operator.             e.g.: "==Abc" will find all preference's value equals to "Abc"
                                 != The not equals operator.         e.g.: "!=Abc" will find all preference's value not equals to "Abc"
                                 ^= The starts-with operator.        e.g.: "^=Abc" will find all preference's value that starts with "Abc"
                                 $= The ends-with operator.          e.g.: "$=Abc" will find all preference's value that ends with "Abc"
                                 *= The constaints operator.         e.g.: "*=Abc" will find all preference's value that contains "Abc" (case-insensitive)
                                 ~= The case insensitive operator.   e.g.: "~=ABC" will find all preference's value that equals to "ABC" (case-insensitive)
     @kwargs['lang']         The filter of the language. Accrording to [MDN Web Doc](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language),
                             it should be the list of accepted language, e.g.: zn_HK, zh_TW, zh, en, *
     '''
     defval=kwargs.get('defval', None)
     user=kwargs.get('owner', kwargs.get('user', None))
     parent=kwargs.get('parent', None)
     value=kwargs.get('value', None)
     langs=kwargs.get('lang', None)
     if langs:
       #Preparing the langs list according to "lang" property: parsing "en;q=0.1, zh;q=0.2, zh_HK;q=0.5, zh_TW;q=0.4, zh_CN;q=0.2" into 
       #   [
       #      {"code":"zh_hk","weight:0.5},
       #      {"code":"zh_TW","weight":0.4},
       #      {"code":"zh","weight":0.2},
       #      {"code":"zh_cn","weight":0.2},
       #      {"code":"en","weight":0.1},
       #   ]
       def parse(s): #Parsing "zh_HK;q=0.1" into {code, weight}
         if ';' in s:
            w=s[s.index(';')+1:].strip()
            s=s[:s.index(';')]
            w=float(re.findall(r'\d*\.\d+|\d+', w)[0])
            return {'code': s.lower(), 'weight': w}
         return {'code': s.lower(), 'weight': 0.1}
       langs=[parse(s.strip()) for s in langs.split(',')]
       langs=sorted(langs, key=lambda ele: ele['weight'], reverse=True)
     if not name: name=kwargs.get('name', None)
     if isinstance(user, str):  user=get_user_model().objects.get(username=user)
     if isUUID(name):
        rst=self.filter(id=name)
     else:
        rst=self.filter(name=name)
     try:
        if user and user.is_authenticated: 
           if len(rst.filter(owner=user))>0:
             rst=rst.filter(owner=user)
           else:
             rst=rst.filter(owner__isnull=True)
        else:
           if not getBool(kwargs.get('config', False)):
              rst=rst.filter(owner__isnull=True)
        if parent: rst=rst.filter(parent=parent)
        if value: 
           value=str(value)
           if value.startswith('=='): 
              rst=rst.filter(value=value[2:].strip())
           elif value.startswith('!='):
              rst=rst.exclude(value=value[2:].strip())
           elif value.startswith('^='):
              rst=rst.filter(value__startswith=value[2:].strip())
           elif value.startswith('$='):
              rst=rst.filter(value__endswith=value[2:].strip())
           elif value.startswith('*='):
              rst=rst.filter(value__icontains=value[2:].strip())
           elif value.startswith('~='):
              rst=rst.filter(value__iexact=value[2:].strip())
           else:
              rst=rst.filter(value=value)
        if langs:
           rst=rst.order_by('owner')
           if not '*' in [l['code'] for l in langs]:
              rst=rst.filter(models.Q(lang__in=[l['code'] for l in langs])|models.Q(lang__isnull=True))
        else:
           rst=rst.order_by('lang', '-owner')
        # parseing the result
        if getBool(kwargs.get('returnQuery', 'False')):
           return rst.query
        if len(rst)>0:
           found=False
           if langs:
              for l in langs:
                 for p in rst:
                    if p.lang==l['code']:
                       rst=p
                       found=True
                       break
                 if found: break
           else:
              #If not specified langs, defualt using the fallback. Otherwise, select the first 
              for p in rst:
                 if p.lang is None:
                    rst=p
                    found=True
                    break
           if not found: rst=rst[0]
        else:
           rst=Preference(name=name, _value=defval)
        if getBool(kwargs.get('returnValue', 'True')):
           return rst.value
        return rst
     except:
      logger.exception('Cannot get preferences<%s>'%name)
      return defval

   def update_or_create(self, *args, **kwargs):
      name=kwargs['name']
      owner=kwargs.get('owner', None)
      if not owner: owner=kwargs.get('user', None)
      try:
         p=Preference.objects.get(name=name, owner=owner)
      except Preference.DoesNotExist:
         p=Preference(name=name, owner=owner)
      p.parent=kwargs.get('parent', None)
      p.sequence=kwargs.get('sequence', 1000)
      p.value=kwargs.get('value', None)
      p.tipe=kwargs.get('tipe', Preference.TYPE_TEXT)
      p.save()
      return p

class AbstractPreference(OrderableValueObject):
   class Meta(object):
      permissions       = (
         ('add_config',  'Can add configuration'),
         ('change_config', 'Can change configuration'),
         ('delete_config', 'Can delete configuration'),
         ('browse_config', 'Can browse system configuration'),
         ('browse_preference', 'Can browse other preferences'),
         ('change_preference_type', 'Can change the preference type'),
      )
      abstract         = True
      unique_together  = [
         ['name', 'lang'],
      ]
      constraints      = [
         models.UniqueConstraint(fields=('name', 'owner'), name='unique_name_and_owner'),
         #models.UniqueConstraint(fields=('name', ), condition=models.Q(owner=None), name='unique_name'),
      ]

   def pref_path(self, filename):
      ext=os.path.splitext(os.path.basename(str(filename)))[1]
      return 'prefs/{0}{1}'.format(self.id, ext)

   TYPE_NONE           = 0 
   TYPE_INT            = 1
   TYPE_DECIMAL        = 2 
   TYPE_BOOLEAN        = 3
   TYPE_TEXT           = 4
   TYPE_RICHTEXT       = 5
   TYPE_URL            = 6
   TYPE_EMAIL          = 7
   TYPE_DATE           = 8
   TYPE_TIME           = 9
   TYPE_DATETIME       = 10
   TYPE_UUIDS          = 11
   TYPE_LIST           = 12
   TYPE_JSON           = 13
   TYPE_FILEPATH       = 14
   TYPES               = (
      (TYPE_NONE, _('webframe.models.Preference.TYPE.NONE')),
      (TYPE_INT, _('webframe.models.Preference.TYPE.INT')),
      (TYPE_DECIMAL, _('webframe.models.Preference.TYPE.DECIMAL')),
      (TYPE_BOOLEAN, _('webframe.models.Preference.TYPE.BOOLEAN')),
      (TYPE_TEXT, _('webframe.models.Preference.TYPE.TEXT')),
      (TYPE_RICHTEXT, _('webframe.models.Preference.TYPE.RICHTEXT')),
      (TYPE_URL, _('webframe.models.Preference.TYPE.URL')),
      (TYPE_EMAIL, _('webframe.models.Preference.TYPE.EMAIL')),
      (TYPE_DATE, _('webframe.models.Preference.TYPE.DATE')),
      (TYPE_TIME, _('webframe.models.Preference.TYPE.TIME')),
      (TYPE_DATETIME, _('webframe.models.Preference.TYPE.DATETIME')),
      (TYPE_UUIDS, _('webframe.models.Preference.TYPE.UUIDS')),
      (TYPE_LIST, _('webframe.models.Preference.TYPE.LIST')),
      (TYPE_JSON, _('webframe.models.Preference.TYPE.JSON')),
      (TYPE_FILEPATH, _('webframe.models.Preference.TYPE.FILEPATH')),
   )

   name                = models.CharField(max_length=100,verbose_name=_('webframe.models.Preference.name'),help_text=_('webframe.models.Preference.name.helptext'))
   _value              = models.TextField(max_length=4096,null=True,blank=True,verbose_name=_('webframe.models.Preference.value'),help_text=_('webframe.models.Preference.value.helptext'))
   owner               = models.ForeignKey(
     settings.AUTH_USER_MODEL,null=True,
     blank=True,
     on_delete=models.CASCADE, #Since Django 2.0, the on_delete field is required.
     related_name='preference_owner',
     verbose_name=_('Pwebframe.models.reference.owner'),
     help_text=_('webframe.models.Preference.owner.helptext'),
   )
   parent              = models.ForeignKey(
     'self',
     null=True,
     blank=True,
     on_delete=models.CASCADE, #Since Django 2.0, the on_delete field is required.
     verbose_name=_('webframe.models.Preference.parent'),
     help_text=_('webframe.models.Preference.parent.helptext'),
   )
   sequence            = models.FloatField(
     default=0.5,
     verbose_name=_('webframe.models.Preference.sequence'),
     help_text=_('webframe.models.Preference.sequence.helptext'),
   )
   _tipe               = models.IntegerField(choices=TYPES, default=TYPE_TEXT, verbose_name=_('webframe.models.Preference.tipe'), help_text=_('webframe.models.Preference.tipe.helptext'))
   encrypted           = models.BooleanField(default=False, verbose_name=_('webframe.models.Preference.encrypted'), help_text=_('webframe.models.Preference.encrypted.helptxt'))
   helptext            = models.TextField(max_length=8192, null=True, blank=True, verbose_name=_('webframe.models.Preference.helptext'), help_text=_('webframe.models.Preference.helptext.helptext'))
   regex               = models.CharField(max_length=1024, default='^.*$', verbose_name=_('webframe.models.Preference.regex'), help_text=_('webframe.models.Preference.regex.helptext'))
   lang                = models.CharField(max_length=20, null=True, blank=True, verbose_name=_('webframe.models.Preference.lang'), help_text=_('webframe.models.Preference.lang.helptext'))
   objects             = PrefManager()

   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.tipe=kwargs['tipe'] if 'tipe' in kwargs else AbstractPreference.TYPE_TEXT
      if 'name' in kwargs: self.name=kwargs['name']
      if 'value' in kwargs: self._value=str(kwargs['value'])
      if 'owner' in kwargs: self.owner=kwargs['owner']
      if 'parent' in kwargs: self.parent=kwargs['parent']
      if 'sequence' in kwargs: self.sequence=kwargs['sequence']
      if 'encrypted' in kwargs: self.encrypted=kwargs['encrypted'] in TRUE_VALUES
      if 'helptext' in kwargs: self.helptext=kwargs['helptext'] 
      if 'regex' in kwargs: self.regex=kwargs['regex']
      if 'lang' in kwargs: self.lang=kwargs['lang']

   @staticmethod
   def get_identifier(name, owner):
      return 'Pref::{0}@{1}'.format(name, owner.id if owner and owner.is_authenticated else 'n/a')

   def __str__(self):
      return AbstractPreference.get_identifier(self.name, self.owner)

   def __unicode__(self):
      return self.__str__

   def __get_ordered_list__(self):
      if hasattr(self.__class__, 'DISABLE_REORDER') or hasattr(settings, 'DISABLE_REORDER'): return None
      if self.parent:
         result=self.__class__.objects.filter(parent=self.parent)
      else:
         result=self.__class__.objects.filter(parent__isnull=True)
      if self.owner: result=result.filter(owner=self.owner)
      return result.order_by('sequence')

   def expDict(self):
      rst=super().expDict()
      rst['tipe']=self._tipe
      rst['encrypted']=self.encrypted
      rst['helptext']=self.helptext
      rst['regex']=self.regex
      return rst

   @property
   def realValue(self):
      return self._value
   @realValue.setter
   def realValue(self, val):
      self._value=val

   @property
   def value(self):
      val=decrypt(self._value) if self.encrypted else self._value
      if self.tipe==AbstractPreference.TYPE_NONE:
         return None
      elif not val:
         return None
      elif self.tipe==AbstractPreference.TYPE_INT or self.tipe==AbstractPreference.TYPE_DECIMAL:
         return int(val)
      elif self.tipe==AbstractPreference.TYPE_BOOLEAN:
         return val in TRUE_VALUES
      elif self.tipe==AbstractPreference.TYPE_TEXT or self.tipe==AbstractPreference.TYPE_RICHTEXT or self.tipe==AbstractPreference.TYPE_EMAIL or self.tipe==AbstractPreference.TYPE_URL:
         return val
      elif self.tipe==AbstractPreference.TYPE_DATE:
         return getTime(val, fmt=FMT_DATE)
      elif self.tipe==AbstractPreference.TYPE_TIME:
         return getTime(val, fmt=FMT_TIME)
      elif self.tipe==AbstractPreference.TYPE_DATETIME:
         return getTime(val, fmt=FMT_DATETIME)
      elif self.tipe==AbstractPreference.TYPE_UUIDS:
         v=re.findall(r'[^,;|]+', val)
         return [uuid.UUID(uid) for uid in v]
      elif self.tipe==AbstractPreference.TYPE_LIST:
         return re.findall(r'[^,;|]+', val)
      elif self.tipe==AbstractPreference.TYPE_JSON:
         return json.loads(val)
      elif self.tipe==AbstractPreference.TYPE_FILEPATH:
         return val
      else:
         raise TypeError('Unknow DataType: {0}'.format(self.tipe))

   @value.setter
   def value(self, val):
      if self.tipe==AbstractPreference.TYPE_NONE:
         val=None
      elif self.tipe==AbstractPreference.TYPE_INT or self.tipe==AbstractPreference.TYPE_DECIMAL:
         val=str(val)
      elif self.tipe==AbstractPreference.TYPE_BOOLEAN:
         val=str(val)
      elif self.tipe==AbstractPreference.TYPE_TEXT or self.tipe==AbstractPreference.TYPE_RICHTEXT or self.tipe==AbstractPreference.TYPE_EMAIL:
         val=str(val)
         if not re.match(self.regex, val): raise ValueError('The value [%s] not match with regex: %s'%(self._value,self.regex))
      elif self.tipe==AbstractPreference.TYPE_DATE:
         if hasattr(val, 'strftime'):
            if not val.tzinfo: val=pytz.utc.localize(val)
         else:
            val=getTime(val, FMT_DATE)
         val=val.strftime(FMT_DATE)
      elif self.tipe==AbstractPreference.TYPE_TIME:
         if hasattr(val, 'strftime'):
            if not val.tzinfo: val=pytz.utc.localize(val)
         else:
            val=getTime(val, FMT_TIME)
         val=val.strftime(FMT_TIME)
      elif self.tipe==AbstractPreference.TYPE_DATETIME:
         if hasattr(val, 'strftime'):
            if not val.tzinfo: val=pytz.utc.localize(val)
         else:
            val=getTime(val, FMT_DATETIME)
         val=val.strftime(FMT_DATETIME)
      elif self.tipe==AbstractPreference.TYPE_UUIDS:
         if hasattr(val, '__iter__'):
            val='|'.join([s for s in val if isUUID(s)])
         else:
            raise ValueError('Expected a list of UUIDs')
      elif self.tipe==AbstractPreference.TYPE_LIST:
         val='|'.join(val) if hasattr(val, '__iter__') else val
      elif self.tipe==AbstractPreference.TYPE_JSON:
         val=json.dumps(val)
      elif self.tipe==AbstractPreference.TYPE_FILEPATH:
         if path:
            if not os.path.isfile(path) and not os.path.isdir(path):
              raise FileNotFoundError(path)

            src=path
            trg=os.path.join(settings.MEDIA_ROOT, self.pref_path(os.path.basename(path)))
            if not os.path.isdir(os.path.dirname(trg)):
               logger.info('Creating the prefs folder: {0}...'.format(trg))
               Path(os.path.dirname(trg)).mkdir(parents=True, exist_ok=True)
            logger.warning('{0} the file: {1} => {2} ...'.format('Replace' if os.path.isfile(trg) else 'Clone', src, trg))
            copyfile(src, trg)
            path=trg
         val=path
      elif self.tipe==AbstractPreference.TYPE_URL:
         from urllib.parse import urlparse
         val=urlparse(val).geturl()

      if not val:
         self._value=None
      else:
         self._value=encrypt(val) if self.encrypted and val else val

   @property
   def asDict(self):
      rst=dict()
      for c in self.childs:
         rst[c.name]=c.realValue
      return rst

   @property
   def childs(self):
      return Preference.objects.filter(parent=self).order_by('sequence', 'name')

   @property
   @deprecated(deprecated_in="v2.8", removed_in="v3.0", current_version="v2.8", details="Use value directly")
   def intValue(self):
      return self.value

   @deprecated(deprecated_in="v2.8", removed_in="v3.0", current_version="v2.8", details="Use value directly")
   @intValue.setter
   def intValue(self, val):
      self.value=val

   @property
   @deprecated(deprecated_in="v2.8", removed_in="v3.0", current_version="v2.8", details="Use value directly")
   def boolValue(self):
      return self.value

   @deprecated(deprecated_in="v2.8", removed_in="v3.0", current_version="v2.8", details="Use value directly")
   @boolValue.setter
   def boolValue(self, val):
      self.value=val

   @property
   @deprecated(deprecated_in="v2.8", removed_in="v3.0", current_version="v2.8", details="Use value directly")
   def datetimeValue(self):
      return self.value

   @deprecated(deprecated_in="v2.8", removed_in="v3.0", current_version="v2.8", details="Use value directly")
   @datetimeValue.setter
   def datetimeValue(self, val):
      self.value=val

   @property
   @deprecated(deprecated_in="v2.8", removed_in="v3.0", current_version="v2.8", details="Use value directly")
   def jsonValue(self):
      return self.value

   @deprecated(deprecated_in="v2.8", removed_in="v3.0", current_version="v2.8", details="Use value directly")
   @jsonValue.setter
   def jsonValue(self, val):
      self.value=val

   @property
   @deprecated(deprecated_in="v2.8", removed_in="v3.0", current_version="v2.8", details="Use value directly")
   def listValue(self):
      return self.value

   @deprecated(deprecated_in="v2.8", removed_in="v3.0", current_version="v2.8", details="Use value directly")
   @listValue.setter
   def listValue(self, val):
      self.value=val

   @property
   def user(self):
      return self.owner
   @user.setter
   def user(self, val):
      self.owner=val

   @property
   @deprecated(deprecated_in="v2.8", removed_in="v3.0", current_version="v2.8", details="Use value directly")
   def pathValue(self):
      return self.value

   @deprecated(deprecated_in="v2.8", removed_in="v3.0", current_version="v2.8", details="Use value directly")
   @pathValue.setter
   def pathValue(self, path):
      self.value=path

   @property
   def tipe(self):
      return self._tipe
   @tipe.setter
   def tipe( self, tipe ):
      '''
      Set the tipe into this preference. 

      @param tipe can be integer value (refer to AbstractPreference.TYPES) or string value;
      '''
      if isinstance(tipe, str):
         ao=['NONE', 'INT', 'DECIMAL', 'BOOLEAN', 'TEXT', 'RICHTEXT', 'URL', 'EMAIL', 'DATE', 'TIME', 'DATETIME', 'UUIDS', 'LIST', 'JSON']
         try:
            tipe=ao.index(tipe.upper().strip())
         except:
            tipe=AbstractPreference.TYPE_TEXT
      elif tipe is None:
         tipe=AbstractPreference.TYPE_TEXT
      if tipe==AbstractPreference.TYPE_EMAIL: 
         self.regex='^[a-zA-Z0-9\._]+@[a-zA-Z0-9\._]{2,}$'
      self._tipe=int(tipe)
   @property
   def tipeName(self):
      return AbstractPreference.TYPES[self.tipe][1]

   def save(self, *args, **kwargs):
      if self._value:
         # If self.encrypted turn on, but not encrypted: e.g.: Read the preference from database, then change the encrypted value
         if self.encrypted and not self._value.startswith(ENCRYPTED_PREFIX):
            #Just encrypte it
            self._value=encrypt(self._value)
         if str(self._value).startswith(ENCRYPTED_PREFIX) and not self.encrypted: #Reversed. If self.encrypted turn off but not encrypted
            self._value=decrypt(self._value)
      if self.lang: self.lang=self.lang.lower()
      super().save(*args, **kwargs)

class Preference(AbstractPreference):

   @property
   def reserved(self):
      return self.helptext != None

   @classmethod
   def pref(self, name, **kwargs):
      return Preference.objects.pref(name, **kwargs)

@receiver(post_delete, sender=Preference)
def cleanFilepath(sender, **kwargs):
   instance=kwargs['instance']
   if instance.tipe==AbstractPreference.TYPE_FILEPATH:
      logger.debug('Catch delete singal on Preference which is FILEPATH.')
      if instance._value and os.path.isfile(instance._value):
         logger.debug('Going to delete: {0}'.format(instance._value))
         os.unlink(instance._value)

@deprecated(deprecated_in="2020-10-01", details="Use Celery-Result instead")
class AsyncManipulationObject(models.Model):
   class Meta(object):
     verbose_name         = _('webframe.models.AsyncManipulationObject')
     verbose_name_plural    = _('webframe.models.AsyncManipulationObjects')
     abstract      = True

   task_id               = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('AsyncManipulationObject.task_id'))

   @property
   def is_processing(self):
     _('AsyncManipulationObject.is_processing')
     return self.task_id is not None

   @property
   def is_ready(self):
     _('AsyncManipulationObject.is_ready')
     return self.task_id is None

class Numbering(ValueObject, AliveObject):
   class Meta(object):
      verbose_name          = _('webframe.models.Numbering')
      verbose_name_plural   = _('webframe.models.Numberings')
      permissions           = [
         ('exec_numbering', 'Can execute the number'),
      ]

   name                    = models.CharField(max_length=100, verbose_name=_('webframe.models.Numbering.name'), help_text=_('webframe.models.Numbering.name.helptxt')) 
   pattern                 = models.CharField(max_length=100, default='{next}', verbose_name=_('webframe.models.Numbering.pattern'), help_text=_('webframe.models.Numbering.pattern.helptxt'))
   next_val                = models.IntegerField(default=0, verbose_name=_('webframe.models.Numbering.next_val'), help_text=_('webframe.models.Numbering.next_val.helptxt'))
   step_val                = models.IntegerField(default=1, verbose_name=_('webframe.models.Numbering.step_val'), help_text=_('webframe.models.Numbering.step_val.helptxt'))

   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      if 'name' in kwargs: self.name=kwargs['name']
      if 'pattern' in kwargs: self.pattern=kwargs['pattern']
      if 'next_val' in kwargs: self.next_val=kwargs['next_val']
      if 'step_val' in kwargs: self.step_val=kwargs['step_val']

   def __str__(self):
      if self.lmd is None:
         return _('webframe.models.Numbering.new')
      return _('webframe.models.Numbering[{name}::{next_val}]').format(name=self.name, next_val=self.next_val)

   def expDict(self):
      rst=super().expDict()
      rst['name']=self.name
      rst['pattern']=self.pattern
      rst['next_val']=self.next_val
      rst['step_val']=self.step_val
      return rst

   @transaction.atomic
   def getNextVal(self, **kwargs):
      '''
      Get the next value and step forward of this numbering.
      Usage: numbering.getNextVal(user='username', now=tz.now(), name='object-name')
      Result:
         if pattern=='INV-{now:%Y%m%d}-{user}-{next:05d}', then return 'INV-20201030-username-00001'

      ** You HAVE TO check permission by yourself **
      '''
      params={**{'now': tz.now(), 'name': self.name}, **kwargs}
      params['next']=self.next_val #The "next" cannot be defined in kwargs
      val=self.pattern.format(**params)
      self.next_val+=self.step_val
      self.save()
      return val
      
   @property
   def next(self):
      '''
      The quick way to get the next value of this numbering. It will auto inject the "now" variable.
      If you want required more options, use @getNextVal(**kwargs) instead.
      '''
      return self.getNextVal(user=get_current_user())

class Profile(ValueObject, AliveObject):
   class Meta(object):
      verbose_name          = _('webframe.models.Profile')
      verbose_name_plural   = _('webframe.models.Profiles')

   user                    = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, verbose_name=_('webframe.models.Profile'), help_text=_('webframe.models.Profile.helptext'))

   @property
   def preferences(self):
      return Preference.objects.filter(owner=self.user, parent__isnull=True).order_by('sequence', 'name')

@receiver(post_save, sender=get_user_model())
def postsave_user(sender, **kwargs):
   if kwargs['created']:
      p=Profile(user=kwargs['instance'])
      p.effDate=getTime('now')
      p.save()

class EnhancedDjangoJSONEncoder(DjangoJSONEncoder):
   def default(self, obj):
      logger.debug('Encoding object with type: {0}'.format(type(obj)))
      if isinstance(obj, uuid.UUID):
         return str(obj)
      return super().default(obj)
