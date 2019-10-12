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
      parser.add_argument('rpts', nargs=1, type=str, default='rpt/*.jrxml', help='The path of those reports (JRXML). Default: rpt/*.html')
      parser.add_argument('--host', dest='host', nargs='?', type=str, default='http://rpthost:8080/', help='The host name of the report server. Default: http://rpthost:8080/')
      parser.add_argument('--role', dest='role', nargs='?', type=str, default='webframe', help='The role to execute the report in reporting server. Default: webframe')
      parser.add_argument('adminuser', nargs='?', type=str, default='jasperadmin', help='The admin username of the report server')
      parser.add_argument('adminpass', nargs='?', type=str, default='jasperadmin', help='The admin password of the report server')

   def handle(self, *args, **kwargs):
      self.kwargs=kwargs
      lv=int(kwargs['verbosity'])
      print('Logging lv: {0}'.format(lv))
      if lv==0:
         logging.basicConfig(level=logging.CRITICAL)
      elif lv==1:
         logging.basicConfig(level=logging.WARNING)
      elif lv==2:
         logging.basicConfig(level=logging.INFO)
      else:
         logging.basicConfig(level=logging.DEBUG)
      logger=logging.getLogger('webframe.commands.deploy')
      self.init_role()
      self.init_user()

   def get(self, path, data):
      auth=(self.kwargs['adminuser'], self.kwargs['adminpass'])
      rep=requests.get('{server}rest_v2{path}'.format(server=self.kwargs['host'], path=path), auth=auth, headers={'Content-Type': 'application/json'}, data=json.dumps(data) if data else '')
      return rep

   def put(self, path, data):
      auth=(self.kwargs['adminuser'], self.kwargs['adminpass'])
      rep=requests.put('{server}rest_v2{path}'.format(server=self.kwargs['host'], path=path), auth=auth, headers={'Content-Type': 'application/json'}, data=json.dumps(data) if data else '')
      return rep
      

   def init_role(self):
      '''
      Init the role.
      '''
      logger.info('Creating/Modifying reporting role: %s ...'%self.kwargs['role'])
      rep=self.get('/roles/{0}'.format(self.kwargs['role']), None)
      if not (200<=rep.status_code<300):
         rep=self.put('/roles/{0}'.format(self.kwargs['role']), data={'name': self.kwargs['role']})
         if 200<=rep.status_code<300:
            logger.info('Role<%s> has been created successfully!'%self.kwargs['role'])
         else:
            logger.warning('Role<%s> cannot been created, status-code: %s'%(self.kwargs['role'], rep.status_code))
            logger.debug(rep.text)
            print(rep.text)
            raise RuntimeError()

   def init_user(self):
      '''
      Init the user
      '''
      # Make sure the user is created.
      kwargs=self.kwargs
      auth=(kwargs['adminuser'], kwargs['adminpass'])
      logger.info('Creating/Updating report user: %s ...'%settings.REPORTING['username'])
      param={
         'fullName': self.kwargs['role'],
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
         raise RuntimeError()
