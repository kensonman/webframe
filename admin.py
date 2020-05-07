# -*- coding: utf-8 -*-
# File:   src/webframe/admin.py
# Date:   2019-11-21 14:55
# Author: Kenson Man <kenson@breakthrough.org.hk>
# Desc:   The file provide the Admin-Tools in webframe module
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _, ugettext
from .models import *
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
   list_display=('id', 'name', 'parent', 'reserved', 'lmb', 'lmd')
   list_filter=('reserved', PreferenceChildParentFilter, 'tipe',)
   search_fields=('name', 'value', 'owner__username', 'owner__username')
   ordering=('owner__username', 'name', 'value')
