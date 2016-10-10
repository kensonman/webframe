from django.conf import settings
from django.db import models
from django.utils import timezone as tz
from django.utils.translation import ugettext_lazy as _
from .CurrentUserMiddleware import get_current_user
import math, uuid

class ValueObject(models.Model):
	class Meta(object):
		abstract		= True
		verbose_name		= _('ValueObject')
		verbose_name_plural	= _('ValueObjects')
		permissions		= ( ('view_%(class)s', 'Can view this model without ownership'), )

	id					= models.UUIDField(
							primary_key=True,
							default=uuid.uuid4,
							editable=False,
							verbose_name=_('ValueObject.id'),
							help_text=_('ValueObject.id.helptext'),
						)
	lmd					= models.DateTimeField(
							auto_now=True,
							verbose_name=_('ValueObject.lmd'),
							help_text=_('ValueObject.lmd.helptext'),
						)
	lmb					= models.ForeignKey(
							settings.AUTH_USER_MODEL,
							default=get_current_user,
							null=True,
							blank=True,
							related_name='%(class)s_lmb',
							verbose_name=_('ValueObject.lmb'),
							help_text=_('ValueObject.lmb.helptext'),
						)
	cd					= models.DateTimeField(
							auto_now_add=True,
							verbose_name=_('ValueObject.cd'),
							help_text=_('ValueObject.cd.helptext'),
						)
	cb					= models.ForeignKey(
							settings.AUTH_USER_MODEL,
							default=get_current_user,
							null=True,
							blank=True,
							related_name='%(class)s_cb',
							verbose_name=_('ValueObject.cb'),
							help_text=_('ValueObject.cb.helptext'),
						)

	def isNew(self):
		return self.lmd is None

	def save(self):
		'''
		Saving the value-object. The method will setup the lmb default value
		'''
		user=get_current_user()
		if not (user or user.is_authenticated()): user=None
		self.lmb=user
		if not self.cb: self.cb=user
		super(ValueObject, self).save()

class AliveObjectManager(models.Manager):
	def living(self):
		now=tz.now()
		return self.filter(enabled=True,effDate__lte=now).filter(models.Q(expDate__isnull=True)|models.Q(expDate__gt=now)).order_by('-effDate')

class AliveObject(models.Model):
	class Meta(object):
		abstract			= True
		verbose_name		= _('AliveObject')
		verbose_name_plural	= _('AliveObjects')
	
	effDate					= models.DateTimeField(
							default=tz.now,
							verbose_name=_('AliveObject.effDate'),
							help_text=_('AliveObject.effDate.helptext'),
						)
	expDate					= models.DateTimeField(
							null=True,
							blank=True,
							verbose_name=_('AliveObject.expDate'),
							help_text=_('AliveObject.expDate.helptext'),
						)
	enabled					= models.BooleanField(
							default=True,
							verbose_name=_('AliveObject.enabled'),
							help_text=_('AliveObject.enabled.helptext'),
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
		if user: rst=rst.filter(owner=user)
		rst=rst.order_by('owner')
		if len(rst)>0:
			return rst[0]
		else:
			return Preference(name=name, value=defval)

class Preference(ValueObject):
	class Meta(object):
		permissions			= (
			('browse_config', 'Can browse system configuration'),
			('browse_preference', 'Can browse other preferences'),
		)
	name					= models.CharField(max_length=100,verbose_name=_('Preference.name'),help_text=_('Preference.name.helptext'))
	value					= models.CharField(max_length=1024,verbose_name=_('Preference.value'),help_text=_('Preference.value.helptext'))
	owner					= models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,related_name='preference_owner',verbose_name=_('Preference.owner'),help_text=_('Preference.owner.helptext'))
	parent					= models.ForeignKey('self',null=True,blank=True,verbose_name=_('Preference.parent'),help_text=_('Preference.parent.helptext'))
	sequence				= models.FloatField(default=0.5,verbose_name=_('Preference.sequence'),help_text=_('Preference.sequence.helptext'))
	objects					= PrefManager()

	def __str__(self):
		return self.value

	def __unicode__(self):
		return self.value

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
