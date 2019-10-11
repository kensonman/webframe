# -*- coding: utf-8 -*-
# 
# File: src/webframe/management/commands/deploy.py
# Date: 2019-09-18 11:29
# Author: Kenson Man <kenson@breakthrough.org.hk>
# Desc: Install the reporting service
# 
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
import logging, requests, json, base64, html

logger=logging.getLogger('webframe.commands.deploy')
b64=lambda path: base64.b64encode(Path(path).read_text().encode('utf-8')).decode('ascii')

class Command(BaseCommand):
   help     = 'Deploy the report(s) into reporting server.'

   def add_arguments(self, parser):
      parser.add_argument('host', nargs=1, type=str, help='The admin username of the report server')
      parser.add_argument('role', nargs=1, type=str, help='The role to access the sitesys report repository')
      parser.add_argument('rpts', nargs=1, type=str, help='The path of those reports (JRXML)', default='rpt/*.jrxml')
      parser.add_argument('adminuser', nargs='?', type=str, help='The admin username of the report server', default='jasperadmin')
      parser.add_argument('adminpass', nargs='?', type=str, help='The admin password of the report server', default='jasperadmin')

   def handle(self, *args, **kwargs):
      self.kwargs=kwargs
      self.init_role()
      self.init_user()

   def get(self, path, data):
      auth=(self.kwargs['adminuser'], self.kwargs['adminpass'])
      rep=requests.get('{server}rest_v2{path}'.format(server=self.kwargs['host'], path=path), auth=auth, headers={'Content-Type': 'application/json'}, data=data)
      return rep

   def put(self, path, data):
      auth=(self.kwargs['adminuser'], self.kwargs['adminpass'])
      rep=requests.put('{server}rest_v2{path}'.format(server=self.kwargs['host'], path=path), auth=auth, headers={'Content-Type': 'application/json'}, data=data)
      return rep
      

   def init_role(self):
      '''
      Init the role.
      '''
      rep=self.get('/roles/{0}'.format(self.kwargs['role']), data={})
      if rep.status_code != 200:
         logger.info('Creating reporting role: %s ...'%kwargs['role'])
         rep=self.put('/roles/{0}'.format(self.kwargs['role']), data={})
         if 200<=rep.status_code<300:
            logger.info('Role<%s> has been created successfully!'%kwargs['role'])
         else:
            logger.warning('Role<%s> cannot been created, status-code: %s'%(kwargs['role'], rep.status_code))
            logger.debug(rep.text)

   def init_user(self):
      '''
      Init the user
      '''
      # Make sure the user is created.
      kwargs=self.kwargs
      auth=(kwargs['adminuser'], kwargs['adminpass'])
      logger.info('Creating/Updating report user: %s ...'%settings.REPORTING['username'])
      param={
         'fullName': 'sitesys system user',
         'enabled': True,
         'password': settings.REPORTING['password'],
         'roles': [ {'name': 'ROLE_USER'}, {'name': kwargs['role']} ],
      }
      param=json.dumps(param).encode('utf-8')
      rep=requests.put(
         '{server}rest_v2/users/{user}'.format(server=settings.REPORTING['server'], user=settings.REPORTING['username'])
         , auth=auth
         , headers={'Content-Type': 'application/json'}
         , data=param
      )
      if 200<=rep.status_code<300:
         logger.info('User<%s> has been created successfully!'%settings.REPORTING['username'])
      else:
         logger.warning('User<%s> cannot been created, status-code: %s'%(settings.REPORTING['username'], rep.status_code))
         logger.debug(rep.text)
         logger.debug(param)
