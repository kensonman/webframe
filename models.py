from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
import math, uuid

class PrefManager(models.Manager):
	def pref(self, name, **kwargs):
		defval=kwargs.get('defval', None)
		user=kwargs.get('user', None)
		rst=self.filter(name=name)
		if user: rst=rst.filter(user=user)
		rst=rst.order_by('user')
		if len(rst)>0:
			return rst[0]
		else:
			return Preference(name=name, value=defval)

class Preference(models.Model):
	id                                      = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name=_('Preference.id'))
	name					= models.CharField(max_length=100)
	value					= models.CharField(max_length=1024)
	user					= models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True)
	parent					= models.ForeignKey('self',null=True,blank=True)
	sequence				= models.FloatField(default=0.5)
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
