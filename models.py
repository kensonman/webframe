from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from .CurrentUserMiddleware import get_current_user
import math, uuid

class ValueObject(models.Model):
	class Meta(object):
		abstract		= True
		verbose_name		= _('ValueObject')
		verbose_name_plural	= _('ValueObjects')

	enabled			= models.BooleanField(default=True, verbose_name=_('ValueObject.enabled'),help_text=_('ValueObject.enabled.helptext'))
	lmb			= models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,related_name='%(class)s_lmd',verbose_name=_('ValueObject.lmb'),help_text=_('ValueObject.lmb.helptext'))
	lmd			= models.DateTimeField(auto_now=True, verbose_name=_('ValueObject.lmd'),help_text=_('ValueObject.lmd.helptext'))

	def isNew(self):
		return self.lmd is None

	def save(self):
		'''
		Saving the value-object. The method will setup the lmb default value
		'''
		user=get_current_user()
		if not (user or user.is_authenticated()): user=None
		self.lmb=user
		super(ValueObject, self).save()

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
	id                                      = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name=_('Preference.id'),help_text=_('Preference.id.helptext'))
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
