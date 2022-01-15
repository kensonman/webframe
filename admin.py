# -*- coding: utf-8 -*-
# File:   src/webframe/admin.py
# Date:   2019-11-21 14:55
# Author: Kenson Man <kenson@breakthrough.org.hk>
# Desc:   The file provide the Admin-Tools in webframe module
from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from ajax_select.fields import AutoCompleteSelectField
from django import forms
from django.contrib import admin
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.safestring import mark_safe
from django.urls import reverse
from django_json_widget.widgets import JSONEditorWidget
from django_summernote.admin import SummernoteModelAdmin
from .models import *
from webframe.templatetags.trim import trim
import logging

logger=logging.getLogger('webframe.admin')

class PreferenceChildParentFilter(admin.SimpleListFilter):
   title=_('webframe.models.Preference.childParentFilter')
   parameter_name='child_parent_filter'

   def lookups(self, req, modelAdmin):
      rst=[
         ('parent', _('webframe.models.Preference.childParentFilter.parent')),
         ('child',  _('webframe.models.Preference.childParentFilter.child')),
      ]
      return rst

   def queryset(self, req, q):
      logger.info('Filtering by PreferenceChildParentFilter: {0}'.format(self.value()))
      if self.value() is None:
         return q
      elif self.value()=='parent':
         return q.filter(id__in=Preference.objects.filter(parent__isnull=False).values('parent__id'))
      else:
         return q.filter(parent__isnull=False)

class AliveObjectEffectiveFilter(admin.SimpleListFilter):
   title=_('webframe.models.AliveObject.effectiveFilter')
   parameter_name='aliveObj_eff_filter'

   def lookups(self, req, modelAdmin):
      rst=[
         ('enabled', _('webframe.models.AliveObject.effectiveFilter.enabled')),
         ('disabled', _('webframe.models.AliveObject.effectiveFilter.disabled')),
         ('effective', _('webframe.models.AliveObject.effectiveFilter.effective')),
         ('coming', _('webframe.models.AliveObject.effectiveFilter.coming')),
         ('comingTmr', _('webframe.models.AliveObject.effectiveFilter.comingTmr')),
         ('comingNextWeek', _('webframe.models.AliveObject.effectiveFilter.comingNextWeek')),
         ('comingNextMonth', _('webframe.models.AliveObject.effectiveFilter.comingNextMonth')),
         ('comingNext3Months', _('webframe.models.AliveObject.effectiveFilter.comingNext3Months')),
         ('expired', _('webframe.models.AliveObject.effectiveFilter.expired')),
      ]
      return rst

   def queryset(self, req, q):
      now=datetime.now()
      value=self.value()
      if value=='enabled':
         return q.filter(enabled=True)
      elif value=='disabled':
         return q.filter(enabled=False)
      elif value=='effective':
         return q.filter(enabled=True, effDate__lte=now).filter(Q(expDate__isNull=True)|Q(expDate__gt=now))
      elif value=='coming':
         return q.filter(enabled=True, effDate__gt=now)
      elif value=='comingTmr':
         now=getTime(now, offset='+1d')
         return q.filter(enabled=True, effDate__lte=now).filter(Q(expDate__isNull=True)|Q(expDate__gt=now))
      elif value=='comingNextWeek':
         now=getTime(now, offset='+7d')
         return q.filter(enabled=True, effDate__lte=now).filter(Q(expDate__isNull=True)|Q(expDate__gt=now))
      elif value=='comingNextMonth':
         now=getTime(now, offset='+1m')
         return q.filter(enabled=True, effDate__lte=now).filter(Q(expDate__isNull=True)|Q(expDate__gt=now))
      elif value=='comingNext3Monts':
         now=getTime(now, offset='+3m')
         return q.filter(enabled=True, effDate__lte=now).filter(Q(expDate__isNull=True)|Q(expDate__gt=now))
      elif value=='expired':
         now=getTime(now, offset='+1d')
         return q.filter(enabled=True, expDate__lte=now)
      return q

class PreferenceInline(admin.TabularInline):
   model    = Preference 
   fields   =['expand', 'sequence', 'name', '_tipe', '_value', 'encrypted']
   readonly_fields=['id', 'cb', 'cd', 'lmb', 'lmd', 'expand']
   extra    =0
   ordering =('parent', 'sequence', 'name')

   def expand(self, obj):
      return mark_safe('[<a href="{0}">Details</a>]'.format(reverse('admin:webframe_preference_change', kwargs={'object_id': obj.id})))
   expand.show_description=_('webframe.models.Preference.expand')

@admin.register(Preference)
class PreferenceAdmin(SummernoteModelAdmin):
   fields=['id', 'parent', 'parent_id', 'sequence', '_tipe', 'owner', 'name', 'lang', 'helptext_', 'regex', '_value', 'filecontent', 'encrypted', 'cb', 'cd', 'lmb', 'lmd']
   form = make_ajax_form(Preference, {
        # fieldname: channel_name
        'parent':  'preferences',
   })
   form=make_ajax_form(Preference, { 'parent': 'preferences', })
   inlines=[
      PreferenceInline,
   ]
   list_display=('id', 'name', 'lang', 'shortValue', 'parent', 'owner', 'lmb', 'lmd')
   list_filter=(PreferenceChildParentFilter, '_tipe', 'encrypted', 'lang')
   ordering=('owner__username', 'name')
   readonly_fields=['id', 'cb', 'cd', 'lmb', 'lmd', 'parent_id', 'regex', 'helptext_']
   search_fields=('name', '_value', 'owner__username')
   summernote_fields=('helptext',)

   def shortValue(self, obj):
      return trim(obj._value, 20)
   shortValue.short_description=_('webframe.models.Preference.value')
   shortValue.admin_order_field='_value'

   def parent_id(self, obj):
      url=reverse('admin:webframe_preference_change', kwargs={'object_id': obj.parent.id})
      return mark_safe('<a href="{1}">{0}</a>'.format(str(obj.parent.id), url))
   parent_id.short_description=_('webframe.models.Preference.parent')

   def helptext_(self, obj):
      return mark_safe(obj.helptext)
   helptext_.short_description=_('webframe.models.Preference.helptext')

   #2021-01-16 16:35, Kenson Man
   #Make the helptext field readonly if and only if superuser
   # Reference: [Django Docs](https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.get_fields)
   def get_fields(self, req, obj=None):
      rst=super().get_fields(req, obj)
      if req.user.is_superuser:
         if 'helptext_' in rst:
            rst[rst.index('helptext_')]='helptext'
      else:
         if 'helptext' in rst:
            rst[rst.index('helptext')]='helptext_'
      return rst

@admin.register(Numbering)
class NumberingAdmin(admin.ModelAdmin):
   fields=('id', 'name', 'desc', 'pattern', 'next_val', 'step_val', 'effDate', 'expDate', 'enabled', 'cb', 'cd', 'lmb', 'lmd')
   list_display=('id', 'name', 'desc', 'pattern', 'effDate', 'expDate', 'enabled', 'lmb', 'lmd')
   list_filter=('enabled', )
   readonly_fields=('id',  'cb', 'cd', 'lmb', 'lmd')
   ordering=('name', )
   search_fields=('name', 'pattern', 'desc')

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
   fields=('id', 'user', 'parent', 'sequence', 'name', 'label', 'icon', 'image', 'effDate', 'expDate', 'onclick', 'mousein', 'mouseout', 'props', 'enabled', 'cb', 'cd', 'lmb', 'lmd')
   formfield_overrides = {
      models.JSONField: {'widget': JSONEditorWidget},
   }

   list_display=('name', 'user', 'parent', 'sequence', 'label', 'effDate', 'expDate', 'enabled', 'cb', 'cd', 'lmb', 'lmd')
   list_filter=('enabled', )
   readonly_fields=('id',  'cb', 'cd', 'lmb', 'lmd')
   ordering=('user', '-parent', 'sequence', 'name')
   search_fields=('id', 'parent__id', 'user__username', 'label', 'parent__label', 'name')

@admin.register(Translation)
class TranslateAdmin(admin.ModelAdmin):
   fields=('id', 'key', 'locale', 'msg', 'pmsg', 'cb', 'cd', 'lmb', 'lmd')
   list_display=('id', 'key', 'locale', 'msg', 'pmsg', 'lmb', 'lmd')
   list_filter=('locale',)
   readonly_fields=('id',  'cb', 'cd', 'lmb', 'lmd')
   ordering=('key', 'locale')
   search_fields=('key', 'locale')

@admin.register(ResetPassword)
class ResetPasswordAdmin(admin.ModelAdmin):
   fields=('id', 'user', 'key', 'effDate', 'expDate', 'enabled', 'request_by', 'complete_date', 'complete_by', 'cb', 'cd', 'lmb', 'lmd')
   list_display=('id', 'user', 'effDate', 'expDate', 'complete_date', 'request_by', 'enabled', 'cb', 'cd', 'lmb', 'lmd')
   list_filter=(AliveObjectEffectiveFilter, )
   readonly_fields=('id',  'key', 'complete_by', 'complete_date', 'request_by', 'cb', 'cd', 'lmb', 'lmd')
   ordering=('user', '-effDate', 'expDate',)
   search_fields=('user__username', )

@admin.register(TokenDetail)
class TokenDetailAdmin(admin.ModelAdmin):
   fields=('id', 'user', 'name', 'token', 'effDate', 'expDate', 'enabled', 'cb', 'cd', 'lmb', 'lmd')
   list_display=('id', 'thisuser', 'name', 'thistoken', 'effDate', 'expDate', 'enabled', 'cb', 'cd', 'lmb', 'lmd')
   list_filter=(AliveObjectEffectiveFilter, )
   readonly_fields=('id', 'cb', 'cd', 'lmb', 'lmd')
   ordering=('token__user', '-effDate', 'expDate',)

   def thisuser(self, obj):
      return obj.token.user
   thisuser.short_description=_('TokenDetail.user')
   thisuser.admin_order_field='token'

   def thistoken(self, obj):
      return obj.token.key
   thistoken.short_description=_('TokenDetail.token')
   thistoken.admin_order_field='token'
