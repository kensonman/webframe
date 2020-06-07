# -*- coding: utf-8 -*-
#
# File: src/webframe/management/commands/pref.py
# Date: 2020-04-22 21:35
# Author: Kenson Man <kenson@kenson.idv.hk>
# Desc: Import / Create / Update / Delete preference
#
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from openpyxl import load_workbook
from pathlib import Path
from webframe.functions import TRUE_VALUES
from webframe.models import Preference
from uuid import UUID
import logging, os, glob


logger=logging.getLogger('webframe.commands.prefs')

class Command(BaseCommand):
   help     = '''Mainpulate the preference in database. Including insert/update/delete/view/import;'''

   def add_arguments(self, parser):
      #Default Value
      pattern='Pref({pref.id}:{pref.name}): {pref.value}'
      action='show'
      max=256
      wildcard='*'
      #Adding arguments
      parser.add_argument('action', type=str, help='The action to be taken. One of import/create/update/delete; Default is {0}'.format(action), default=action)
      parser.add_argument('--name', dest='name', type=str, help='The name of the preference. Optional when import, otherwise required;', default=None)
      parser.add_argument('--value', dest='value', type=str, help='The value of the preference. Required when create/update;', default=None)
      parser.add_argument('--owner', dest='owner', type=str, help='The owner of the preference. Optional;', default=None)
      parser.add_argument('--parent', dest='parent', type=str, help='The parent\'s name of the preference. Optional;', default=None)
      parser.add_argument('--reserved', dest='reserved', action='store_true', help='The reserved indicator of the preference. Used at insert/update; Optional; Default False')
      parser.add_argument('--file', dest='file', type=str, help='The file (or directory) to be import. Required when import', default=None)
      parser.add_argument('--pattern', dest='pattern', type=str, help='The output pattern. {0}'.format(pattern), default=pattern)
      parser.add_argument('--max', dest='max', type=int, help='The maximum number of preference to show. Default is {0}'.format(max), default=max)
      parser.add_argument('--wildcard', dest='wildcard', type=str, help='Specify the wildcard; Default is {0}'.format(wildcard), default=wildcard)
      parser.add_argument('--force', '-f ', dest='force', action='store_true', help='Force the import', default=False)

   def __get_owner__(self, owner=None):
      owner=owner if owner else self.kwargs['owner']
      return get_user_model().objects.get(username=owner) if owner else None

   def __get_parent__(self, parent=None):
      parent=parent if parent else self.kwargs['parent']
      if parent:
         try:
            #Get parent by uuid
            return Preference.objects.get(id=parent)
         except:
            try:
               #Get parent by name
               return Preference.objects.get(name=parent)
            except:
               pass
      return None

   def __get_pref__(self, owner=None, parent=None):
      owner=owner if owner else self.__get_owner__()
      parent=parent if parent else self.__get_parent__()
      if self.kwargs['parent'] and parent==None:
         raise Preference.DoesNotExist('Parent Preference not found: {0}'.format(self.kwargs['parent']))

      rst=Preference.objects.filter(name=self.kwargs['name'])
      if owner:
         rst=rst.filter(owner=owner)
      else:
         rst=rst.filter(owner__isnull=True)

      if parent:
         rst=rst.filter(parent=parent)
      else:
         rst=rst.filter(parent__isnull=True)

      size=len(rst)
      if size<1:
         raise Preference.DoesNotExist
      elif size>1:
         raise MultipleObjectsReturned
      else:
         return rst[0]

   def output( self, pref, pattern=None ):
      pattern=pattern if pattern else self.kwargs['pattern']
      print(pattern.format(pref=pref))
      pattern='   {0}'.format(pattern)
      for ch in pref.childs:
         self.output(ch, pattern)

   def handle(self, *args, **kwargs):
      verbosity=int(kwargs['verbosity'])
      if verbosity==3:
         logger.setLevel(logging.DEBUG)
      elif verbosity==2:
         logger.setLevel(logging.INFO)
      elif verbosity==1:
         logger.setLevel(logging.WARNING)
      else:
         logger.setLevel(logging.ERROR)
      self.kwargs=kwargs

      action=kwargs['action']
      if action=='import':
         self.imp()
      elif action=='create':
         self.create()
      elif action=='update':
         self.update()
      elif action=='delete':
         self.delete()
      elif action=='show':
         self.show()
      else:
         logger.warning('Unknown action: {0}'.format(action))
      logger.info('DONE!')

   def show(self):
      logger.info('Showing the preference ...')
      q=Preference.objects.all()

      if self.kwargs['name']:
         logger.info('   with the name filter: {0}'.format(self.kwargs['name']))
         if self.kwargs['wildcard'] in self.kwargs['name']:
            q=q.filter(name__icontains=self.kwargs['name'].replace(self.kwargs['wildcard'], ''))
         else:
            q=q.filter(name=self.kwargs['name'])

      if self.kwargs['value']:
         logger.info('   with the value filter: {0}'.format(self.kwargs['value']))
         q=q.filter(value__icontains=self.kwargs['value'])

      if self.kwargs['owner']:
         logger.info('   which belongs to user: {0}'.format(self.kwargs['owner']))
         q=q.filter(owner__username=self.kwargs['owner'])

      if self.kwargs['parent']:
         logger.info('   which belongs to preference: {0}'.format(self.kwargs['parent']))
         q=q.filter(parent__name__iexact=self.kwargs['parent'])
      else:
         q=q.filter(parent__isnull=True)

      if 'reserved' in self.kwargs:
         logger.info('   which {0} system reserved'.format('is' if self.kwargs['reserved'] else 'is not'))
         q=q.filter(reserved=self.kwargs['reserved'])

      for p in q:
         self.output(p)
      logger.warning('There have {0} preference(s) has been shown'.format(len(q)))

   def create(self):
      owner=self.__get_owner__()
      parent=self.__get_parent__()
      with transaction.atomic():
         try:
            self.__get_pref__(owner, parent)
            logger.warning('The specified preference already exists, discard all changes')
         except Preference.DoesNotExist:
            p=Preference(name=self.kwargs['name'], value=self.kwargs['value'], owner=owner, parent=parent)
            p.save()
            logger.info('The preference<{0}> has been created with value: {1}'.format(p.name, p.value))

   def update(self):
      owner=self.__get_owner__()
      parent=self.__get_parent__()
      with transaction.atomic():
         try:
            pref=self.__get_pref__(owner, parent)
            pref.value=self.kwargs['value']
            pref.save()
            logger.info('Preference has been updated')
            self.output(pref)
         except Preference.DoesNotExist:
            Preference(name=self.kwargs['name'], value=self.kwargs['value'], owner=owenr, parent=parent).save()
            logger.info('Preference has been created')

   def delete(self):
      pref=self.__get_pref__()
      pref.delete()
      logger.warning('Preference has been deleted')

   def impfile( self, f ):
      if os.path.isfile(f) and os.access(f, os.R_OK):
         logger.info('Importing file: {0}'.format(f))
      else:
         logger.warning('The file is not readable: {0}'.format(f))
         return

      wb=load_workbook(filename=f)
      ws=wb.active
      logger.debug('   Importing worksheet: {0}'.format(ws.title))
      cnt=0
      with transaction.atomic():
         for r in range(1, ws.max_row+1):
            name=ws.cell(row=r, column=1).value
            if r==1 and (name.upper()=='ID' or name.upper()=='NAME'): continue #Skip the first row if header row
            val=ws.cell(row=r, column=2).value
            parent=self.__get_parent__(ws.cell(row=r, column=3).value)
            owner=self.__get_owner__(ws.cell(row=r, column=4).value)
            reserved=ws.cell(row=r, column=5).value in TRUE_VALUES
            logger.debug('     Importing row: {0}: {1} ({2})'.format(r, name, 'reserved' if reserved else 'normal'))
            #ID/NAME,VALUES,PARENT,OWNER,RESERVED
            try:
               self.kwargs['name']=name
               pref=self.__get_pref__(owner, parent)
               pref.value=val
               pref.reserved=reserved
               pref.save()
            except Preference.DoesNotExist:
               Preference(name=name, value=val, owner=owner, parent=parent, reserved=reserved).save()
            cnt+=1
      logger.debug('   Imported {0} row(s)'.format(cnt))

   def impdir( self, d ):
      if os.path.isdir(d):
         logger.info('Importing directory: {0}'.format(d))
      else:
         logger.warning('This is not the directory: {0}'.format(d))
         return

      cnt=0
      with transaction.atomic():
         p=Preference.objects.pref('IMPORTED_PREFERENCES', returnValue=False)
         p.reserved=True
         p.save()
         for f in glob.glob(os.path.join(d, '*.xlsx')):
            try:
               Preference.objects.get(name=f, parent=p, reserved=True)
               if self.kwargs['force']:
                  self.impfile( f )
                  cnt+=1
            except Preference.DoesNotExist:
               self.impfile( f )
               cnt+=1
               Preference(name=f, reserved=True, parent=p).save()
      logger.debug('Imported {0} file(s)'.format(cnt))

   def imp(self):
      f=self.kwargs['file']
      if os.path.isdir(f):
         self.impdir(f)
      elif os.path.isfile(f):
         self.impfile(f)
