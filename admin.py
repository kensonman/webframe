# -*- coding: utf-8 -*-
# File:   src/webframe/admin.py
# Date:   2019-11-21 14:55
# Author: Kenson Man <kenson@breakthrough.org.hk>
# Desc:   The file provide the Admin-Tools in webframe module
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _, ugettext
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

@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
   fields=('id', 'name', 'tipe', 'parent', 'owner', '_value', 'reserved', 'encrypted', 'cb', 'cd', 'lmb', 'lmd')
   list_display=('id', 'name', 'shortValue', 'parent', 'owner', 'reserved', 'lmb', 'lmd')
   list_filter=('reserved', PreferenceChildParentFilter, 'tipe', 'encrypted')
   readonly_fields=('id',  'cb', 'cd', 'lmb', 'lmd')
   ordering=('owner__username', 'name')
   search_fields=('name', '_value', 'owner__username')

   def shortValue(self, obj):
      return trim(obj._value, 20)
   shortValue.short_description=_('webframe.models.Preference.value')
   shortValue.admin_order_field='_value'

@admin.register(Numbering)
class NumberingAdmin(admin.ModelAdmin):
   fields=('id', 'name', 'pattern', 'next_val', 'step_val', 'effDate', 'expDate', 'enabled', 'cb', 'cd', 'lmb', 'lmd')
   list_display=('id', 'name', 'pattern', 'effDate', 'expDate', 'enabled', 'lmb', 'lmd')
   list_filter=('enabled', )
   readonly_fields=('id',  'cb', 'cd', 'lmb', 'lmd')
   ordering=('name', )
   search_fields=('name', 'pattern',)
