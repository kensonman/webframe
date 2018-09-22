from datetime import datetime
from deprecation import deprecated
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone as tz
from django.shortcuts import get_object_or_404 as getObj
from django.utils.translation import ugettext_lazy as _
from json import JSONEncoder
from .CurrentUserMiddleware import get_current_user
from .functions import getBool, getClass
import math, uuid, logging, json

logger=logging.getLogger('webframe.models')

DATEFMT='%Y-%m-%d %H:%M:%S.%fT%z'
fmt=lambda d: 'null' if d is None else d.strftime(DATEFMT)
rfmt=lambda d: None if d=='null' else datetime.strptime(d, DATEFMT)
nullValue=_('null') #Make sure the null value can be translate

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
   elif typ is 'BooleanField':
     return getBool(val)
   elif typ in ['UUIDField']:
     return uuid.UUID(val)
   elif typ in ['CharField', 'TextField', 'EmailField', 'URLField']:
     return str(val)
   elif typ is 'DateTimeField':
     return datetime.strptime(val, DATEFMT)
   elif typ is 'ForeignKey':
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
     if not Dictable.META_TYPE in data: raise TypeError('This is not the dictionary created by asDict. No type information found')
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

class ValueObject(models.Model, Dictable):
   CACHED='__CACHED__'

   class Meta(object):
     abstract      = True
     verbose_name      = _('webframe.models.ValueObject')
     verbose_name_plural = _('webframe.models.ValueObjects')
     permissions    = ( ('view_%(class)s', 'Can view this model without ownership'), )

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

   def isNew(self):
      return self.lmd is None

   def isNotNew(self):
      return self.lmd is not None

   def id_or_new(self):
      if self.isNew():
         return 'new'
      return self.id.hex

   @deprecated(deprecated_in="v2.1", removed_in="v2.2", current_version="v2.1", details="Use Dictable.expDict() instead")
   def asDict(self):
     return {'id': self.id.hex, 'lmd':fmt(self.lmd), 'lmb':self.lmb.username, 'cd':fmt(self.cd), 'cb':self.cb.username}

   @deprecated(deprecated_in="v2.1", removed_in="v2.2", current_version="v2.1", details="Use Dictable.impDict(data) instead")
   def fromDict(self, data):
     self.id=data['id']
     self.lmd=rfmt(data['lmd'])
     self.lmb=getObj(get_user_model(), username=data['lmb'])
     self.cd=rfmt(data['cd'])
     self.cb=getObj(get_user_model(), username=data['cb'])

   def save(self):
      '''
      Saving the value-object. The method will setup the lmb default value
      '''
      user=get_current_user()
      if user:
         if not user.is_authenticated: user=None
      self.lmb=user
      try:
         if not self.cb: self.cb=user
      except TypeError:
         self.cb=user
      super(ValueObject, self).save()

   def cached(self, name, fn, useCache=True):
     '''
     Retrieve the value from cache. This is used to cache and retrieve the specific data from the object cache. 
     If the specific data is existed, the function will return the cached value directly. Otherwise, the fn will be invited
     and save the result as a cache for next time.

     @param name The name of the cache
     @param fn The target function to retrieve the value. e.g.: lambda: self.__class__.objects.filter(id=123)
     @param useCache Force to clear the cache when this is Flase
     '''
     if not hasattr(self, ValueObject.CACHED): setattr(self, ValueObject.CACHED, dict()) #Create the cache dict if not exists
     c=getattr(self, ValueObject.CACHED) #Retrieve the caches
     if (not useCache) and name in c: del c[name] #Remove the cache if not useCache

     if name not in c: c[name]=fn()

     return c[name]

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
      '''
      return self.filter(effDate__lte=end).filter(models.Q(expDate__isnull=True)|models.Q(expDate__gte=start))

class AliveObject(models.Model, Dictable):
   class Meta(object):
      abstract         = True
      verbose_name      = _('webframe.models.AliveObject')
      verbose_name_plural = _('webframe.models.AliveObjects')
   
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

class PrefManager(models.Manager):
   def pref(self, name, **kwargs):
     '''
     Get the preference from database.
     
     @name                   The preference name
     @kwargs['defval']       The default value
     @kwargs['user']         The preference owner
     @kwargs['returnValue']  The boolean value indicate the method return the preference's value instead of preference instance.
     @kwargs['parent']       The parent preference of this instance
     '''
     defval=kwargs.get('defval', None)
     user=kwargs.get('user', None)
     parent=kwargs.get('parent', None)
     rst=self.filter(name=name)
     try:
      if user: 
         if len(rst.filter(owner=user))>0:
           rst=rst.filter(owner=user)
      if parent: rst=rst.filter(parent=parent)
      rst=rst.order_by('owner')
      if len(rst)>0:
         rst=rst[0]
      else:
         rst=Preference(name=name, value=defval)
      if str(kwargs.get('returnValue', 'False')).upper() in ['TRUE', 'T', 'YES', 'Y', '1', 'ON']:
         return rst.value
      return rst
     except:
      logger.exception('Cannot get preferences<%s>'%name)
      return defval

class Preference(ValueObject):
   class Meta(object):
      permissions       = (
         ('add_config',  'Can add configuration'),
         ('change_config', 'Can change configuration'),
         ('delete_config', 'Can delete configuration'),
         ('browse_config', 'Can browse system configuration'),
         ('browse_preference', 'Can browse other preferences'),
      )
   name               = models.CharField(max_length=100,verbose_name=_('webframe.models.Preference.name'),help_text=_('webframe.models.Preference.name.helptext'))
   value               = models.CharField(max_length=1024,verbose_name=_('webframe.models.Preference.value'),help_text=_('webframe.models.Preference.value.helptext'))
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
   objects             = PrefManager()

   def __str__(self):
      return '(None)' if self.value is None else "{0}::{1}".format(self.name, self.value)

   def __unicode__(self):
      return '(None)' if self.value is None else "{0}::{1}".format(self.name, self.value)

   @property
   def childs(self):
      return Preference.objects.filter(parent=self).order_by('sequence')

   def save(self):
      if self.parent:
         self.sequence-=0.1
         super(Preference, self).save()
         childs=Preference.objects.filter(parent=self.parent).order_by('sequence')
         cnt=0
         for p in childs:
            cnt+=1
            p.sequence=cnt
            super(Preference, p).save()
      else:
         self.sequence=math.ceil(self.sequence)
         super(Preference, self).save()

class Privilege(models.Model):
   class Meta(object):
     verbose_name         = _('webframe.models.Privilege')
     verbose_name_plural    = _('webframe.models.Privileges')

   contenttype          = models.ForeignKey(
     ContentType, 
     on_delete=models.CASCADE, #Since Django 2.0, the on_delete field is required.
   )
   name               = models.CharField(max_length=50,verbose_name=_('webframe.models.Privilege.name'))
   desc               = models.TextField(max_length=200,null=True,blank=True,verbose_name=_('webframe.models.Privilege.desc'))

class GrantedPrivilege(models.Model):
   class Meta(object):
     verbose_name         = _('webframe.models.GrantedPrivilege')
     verbose_name_plural    = _('webframe.models.GrantedPrivilege')

   owner               = models.ForeignKey(
     settings.AUTH_USER_MODEL,
     on_delete=models.CASCADE, #Since Django 2.0, the on_delete field is required.
     verbose_name=_('webframe.models.GrantedPrivilege.owner'),
   )
   privilege            = models.ForeignKey(
     Privilege,
     on_delete=models.CASCADE, #Since Django 2.0, the on_delete field is required.
     verbose_name=_('webframe.models.GrantedPrivilege.privilege'),
   )
   item               = models.UUIDField(verbose_name=_('webframe.models.GrantedPrivilege.item'))
   
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

# The abstract value=object that provide the sequence field and related ordering features
class OrderableValueObject(ValueObject):
   sequence      = models.FloatField(default=1,verbose_name=_('webframe.models.OrderableValueObject.sequence'))

   class Meta:
      abstract   = True
      ordering   = ['sequence', 'id',]

   # Get the ordering features
   def __get_ordered_list__(self):
      return self.__class__.objects.all().order_by('sequence')

   # Saving and reorder the models
   def save(self):
      if not self.sequence: self.sequence=1
      self.sequence-=0.5
      ValueObject.save(self)
      counter=1
      for i in self.__get_ordered_list__():
         i.sequence=counter
         counter+=1
         ValueObject.save(i)
