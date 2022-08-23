# -*- coding: utf-8 -*-
# 
# File:     webframe/tables.py
# Date:     2018-10-07 17:54
# Author:   Kenson Man <kenson@kenson.idv.hk>
# Desc:     Provide the tables for webframe tables
#
from django_tables2 import A
from django.contrib.auth.models import User
from django.utils.html import mark_safe, escape 
from django.utils.translation import ugettext_lazy as _
from .models import *

import django_tables2 as tables, logging
logger=logging.getLogger('webframe.tables')

class PreferenceTable(tables.Table):
   name=tables.LinkColumn('webframe:pref', args=[A('owner.username'), A('id.hex')])

   class Meta(object):
      model=Preference
      fields=('name', 'sequence', 'value')
      attrs={  'class': 'table', }
      row_attrs={ 'prefId': lambda record: record.id.hex }

   def render_value(self, value):
      value=escape(value)
      if len(value)>100:
         value='<i class="fas fa-align-left"></i>'
      elif len(value)>50: 
         value='{0}<span class="more-text">...</span>{1}'.format(value[0:10], value[-10:])
      return mark_safe('<span class="value">{0}</span>'.format(value))

class UserTable(tables.Table):
   username=tables.LinkColumn('webframe:user', args=[A('username'),])

   class Meta(object):
      model=User
      fields=('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined')
      attrs={  'class': 'table', }
      row_attrs={ 'username': lambda record: record.username, 'userId': lambda record: record.id}

class WebAuthnPubkeyTable(tables.Table):
   actions=tables.TemplateColumn(verbose_name=_('actions'), template_name='webframe/pubkeys-actionsColumn.html', orderable=False) # orderable not sortable
   pkey=tables.Column(accessor=A('pubkey'))
   ipaddr=tables.LinkColumn('webframe:ipgeo', args=[A('ipaddr')])

   class Meta(object):
      model=WebAuthnPubkey
      fields=('displayName', 'pkey', 'lastSignin', 'ipaddr', 'cb', 'cd')
      attrs={  'class':'table', 'id':'WebAuthnPubkeyTbl'}
      row_attrs={ 'id': lambda record:record.id, 'ipaddr':lambda record:record.ipaddr }

   def render_pkey(self, value):
      if value==None:
         return None
      elif len(value)<10:
         return value
      else:
         return '{0}...{1}'.format(value[0:6], value[-4:])
