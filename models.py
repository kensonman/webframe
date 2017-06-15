from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone as tz
from django.utils.translation import ugettext_lazy as _
from .CurrentUserMiddleware import get_current_user
import math, uuid, logging

logger=logging.getLogger('webframe.models')

class ValueObject(models.Model):
   CACHED='__CACHED__'

   class Meta(object):
      abstract        = True
      verbose_name        = _('webframe.models.ValueObject')
      verbose_name_plural = _('webframe.models.ValueObjects')
      permissions     = ( ('view_%(class)s', 'Can view this model without ownership'), )

   id                  = models.UUIDField(
      primary_key=True,
      default=uuid.uuid4,
      editable=False,
      verbose_name=_('webframe.models.ValueObject.id'),
      help_text=_('webframe.models.ValueObject.id.helptext'),
   )
   lmd                 = models.DateTimeField(
      auto_now=True,
      verbose_name=_('webframe.models.ValueObject.lmd'),
      help_text=_('webframe.models.ValueObject.lmd.helptext'),
   )
   lmb                 = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      default=get_current_user,
      null=True,
      blank=True,
      related_name='%(class)s_lmb',
      verbose_name=_('webframe.models.ValueObject.lmb'),
      help_text=_('webframe.models.ValueObject.lmb.helptext'),
   )
   cd                  = models.DateTimeField(
      auto_now_add=True,
      verbose_name=_('webframe.models.ValueObject.cd'),
      help_text=_('webframe.models.ValueObject.cd.helptext'),
   )
   cb                  = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      default=get_current_user,
      null=True,
      blank=True,
      related_name='%(class)s_cb',
      verbose_name=_('webframe.models.ValueObject.cb'),
      help_text=_('webframe.models.ValueObject.cb.helptext'),
   )

   def isNew(self):
        return self.lmd is None

   def id_or_new(self):
        if self.isNew():
            return 'new'
        return self.id.hex

   def save(self):
        '''
        Saving the value-object. The method will setup the lmb default value
        '''
        user=get_current_user()
        if user:
            if not user.is_authenticated(): user=None
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

class AliveObject(models.Model):
    class Meta(object):
        abstract            = True
        verbose_name        = _('webframe.models.AliveObject')
        verbose_name_plural = _('webframe.models.AliveObjects')
    
    effDate                 = models.DateTimeField(
                            default=tz.now,
                            verbose_name=_('webframe.models.AliveObject.effDate'),
                            help_text=_('webframe.models.AliveObject.effDate.helptext'),
                        )
    expDate                 = models.DateTimeField(
                            null=True,
                            blank=True,
                            verbose_name=_('webframe.models.AliveObject.expDate'),
                            help_text=_('webframe.models.AliveObject.expDate.helptext'),
                        )
    enabled                 = models.BooleanField(
                            default=True,
                            verbose_name=_('webframe.models.AliveObject.enabled'),
                            help_text=_('webframe.models.AliveObject.enabled.helptext'),
                        )

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
        

class PrefManager(models.Manager):
    def pref(self, name, **kwargs):
      defval=kwargs.get('defval', None)
      user=kwargs.get('user', None)
      rst=self.filter(name=name)
      try:
        if user: rst=rst.filter(owner=user)
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
        permissions         = (
            ('add_config',  'Can add configuration'),
            ('change_config', 'Can change configuration'),
            ('delete_config', 'Can delete configuration'),
            ('browse_config', 'Can browse system configuration'),
            ('browse_preference', 'Can browse other preferences'),
        )
    name                    = models.CharField(max_length=100,verbose_name=_('webframe.models.Preference.name'),help_text=_('webframe.models.Preference.name.helptext'))
    value                   = models.CharField(max_length=1024,verbose_name=_('webframe.models.Preference.value'),help_text=_('webframe.models.Preference.value.helptext'))
    owner                   = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,related_name='preference_owner',verbose_name=_('Pwebframe.models.reference.owner'),help_text=_('webframe.models.Preference.owner.helptext'))
    parent                  = models.ForeignKey('self',null=True,blank=True,verbose_name=_('webframe.models.Preference.parent'),help_text=_('webframe.models.Preference.parent.helptext'))
    sequence                = models.FloatField(default=0.5,verbose_name=_('webframe.models.Preference.sequence'),help_text=_('webframe.models.Preference.sequence.helptext'))
    objects                 = PrefManager()

    def __str__(self):
        return '(None)' if self.value is None else str(self.value)

    def __unicode__(self):
        return '(None)' if self.value is None else unicode(self.value)

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
        verbose_name            = _('webframe.models.Privilege')
        verbose_name_plural     = _('webframe.models.Privileges')

    contenttype             = models.ForeignKey(ContentType)
    name                    = models.CharField(max_length=50,verbose_name=_('webframe.models.Privilege.name'))
    desc                    = models.TextField(max_length=200,null=True,blank=True,verbose_name=_('webframe.models.Privilege.desc'))

class GrantedPrivilege(models.Model):
    class Meta(object):
        verbose_name            = _('webframe.models.GrantedPrivilege')
        verbose_name_plural     = _('webframe.models.GrantedPrivilege')

    owner                   = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name=_('webframe.models.GrantedPrivilege.owner'))
    privilege               = models.ForeignKey(Privilege,verbose_name=_('webframe.models.GrantedPrivilege.privilege'))
    item                    = models.UUIDField(verbose_name=_('webframe.models.GrantedPrivilege.item'))
    
