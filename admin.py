# -*- coding: utf-8 -*-
# File:   src/webframe/admin.py
# Date:   2019-11-21 14:55
# Author: Kenson Man <kenson@breakthrough.org.hk>
# Desc:   The file provide the Admin-Tools in webframe module
from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from ajax_select.fields import AutoCompleteSelectField
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.safestring import mark_safe
from django.urls import reverse
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
   fields=('id', 'parent', 'parent_id', '_tipe', 'owner', 'name', 'helptext_', 'regex', '_value', 'encrypted', 'cb', 'cd', 'lmb', 'lmd')
   form = make_ajax_form(Preference, {
        # fieldname: channel_name
        'parent':  'preferences',
   })
   form=make_ajax_form(Preference, { 'parent': 'preferences', })
   inlines=[
      PreferenceInline,
   ]
   list_display=('id', 'name', 'shortValue', 'parent', 'owner', 'lmb', 'lmd')
   list_filter=(PreferenceChildParentFilter, '_tipe', 'encrypted')
   ordering=('owner__username', 'name')
   readonly_fields=('id', 'cb', 'cd', 'lmb', 'lmd', 'parent_id', 'regex', 'helptext_')
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

@admin.register(Numbering)
class NumberingAdmin(admin.ModelAdmin):
   fields=('id', 'name', 'pattern', 'next_val', 'step_val', 'effDate', 'expDate', 'enabled', 'cb', 'cd', 'lmb', 'lmd')
   list_display=('id', 'name', 'pattern', 'effDate', 'expDate', 'enabled', 'lmb', 'lmd')
   list_filter=('enabled', )
   readonly_fields=('id',  'cb', 'cd', 'lmb', 'lmd')
   ordering=('name', )
   search_fields=('name', 'pattern',)
