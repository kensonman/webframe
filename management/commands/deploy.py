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
import logging, requests, json, base64, html, glob
try:
   import xml.etree.cElementTree as ET
except ImportError:
   import xml.etree.ElementTree as ET

logger=logging.getLogger('webframe.commands.deploy')
b64=lambda path: base64.b64encode(Path(path).read_text().encode('utf-8')).decode('ascii')
ns={'jr': 'http://jasperreports.sourceforge.net/jasperreports',}

class Command(BaseCommand):
   help     = 'Deploy the report(s) into reporting server.'

   def add_arguments(self, parser):
      parser.add_argument('dbcon', nargs=1, type=str, default='./rpt/MyReports/DBConn.xml', help='The path of DBConnection declaration (XML). Default: .rpt/MyReports/DBConn.xml')
      parser.add_argument('rpts', nargs='+', type=str, default='./rpt/MyReports/*.jrxml', help='The path of those reports (JRXML). Default: .rpt/MyReports/*.jrxml')
      parser.add_argument('--folder', dest='folder', nargs='?', type=str, default=settings.REPORTING['username'], help='The folder to store all imported resources. Default: {0}'.format(settings.REPORTING['username']))
      parser.add_argument('--host', dest='host', nargs='?', type=str, default='http://rpthost:8080/', help='The host name of the report server. Default: http://rpthost:8080/')
      parser.add_argument('--role', dest='role', nargs='?', type=str, default='webframe', help='The role to execute the report in reporting server. Default: webframe')
      parser.add_argument('adminuser', nargs='?', type=str, default='jasperadmin', help='The admin username of the report server')
      parser.add_argument('adminpass', nargs='?', type=str, default='jasperadmin', help='The admin password of the report server')

   def handle(self, *args, **kwargs):
      '''
      Executing the command.
      '''
      self.kwargs=kwargs
      lv=int(kwargs['verbosity'])
      print('Logging lv: {0}'.format(lv))
      if lv==0:
         logger.setLevel(logging.ERROR)
      elif lv==1:
         logger.setLevel(logging.WARNING)
      elif lv==2:
         logger.setLevel(logging.INFO)
      else:
         logger.setLevel(logging.DEBUG)
      self.init_role()
      self.init_user()

      self.import_file(self.kwargs['dbcon'])

      count=0
      for p in self.kwargs['rpts']:
         for f in glob.glob(p):
            count+=1
            self.import_file(f)
      if count>0:
         logger.info('DONE! Imported {0} file(s).'.format(count))
      else:
         logger.warning('Cannot found any matched file(s): {0}'.format(self.kwargs['rpts']))

   def get(self, path, data):
      '''
      The shortcut to query report server.
      '''
      auth=(self.kwargs['adminuser'], self.kwargs['adminpass'])
      rep=requests.get('{server}rest_v2{path}'.format(server=self.kwargs['host'], path=path), auth=auth, headers={'Content-Type': 'application/json'}, data=json.dumps(data) if data else '')
      return rep

   def put(self, path, data):
      '''
      The shortcut to query report server.
      '''
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
      logger.info('Creating/Updating report user: %s ...'%settings.REPORTING['username'])
      param={
         'fullName': self.kwargs['role'],
         'enabled': True,
         'password': settings.REPORTING['password'],
         'roles': [ {'name': 'ROLE_USER'}, {'name': self.kwargs['role']} ],
      }
      rep=self.put('/users/{0}'.format(settings.REPORTING['username']), data=param)
      if 200<=rep.status_code<300:
         logger.info('User<%s> has been created successfully!'%settings.REPORTING['username'])
      else:
         logger.warning('User<%s> cannot been created, status-code: %s'%(settings.REPORTING['username'], rep.status_code))
         logger.debug(rep.text)
         logger.debug(param)
         raise RuntimeError()

   def import_file(self, filepath):
      '''
      Importing the specified file into report server. It will parse the XML and process it automatically.
      '''
      logger.info('Importing report: {0}...'.format(filepath))
      with open(filepath, 'r') as f:
         content=f.read()
      root=ET.fromstring(content)
      if root.tag == 'jdbcDataAdapter':
         param={
            'uri': '/{0}/DBConn'.format(self.kwarg['folder']),
            'label': root.find('name').text,
            'description': 'The database connection when generating report',
            'permissionMask': '0',
            'version': '1',

            'driverClass': root.find('driver').text,
            'username': root.find('username').text, #Refer to rpt/createUser.sql
            'password': root.find('password').text, #Refer to rpt/createUser.sql
            'connectionUrl': root.find('url').text,
         }
         self.create_resource(self, 'application/repository.jdbcDataSource+json', param)
      elif root.tag=='{'+ns['jr']+'}jasperReport':
         pass


   def create_resource(self, tipe, param):
      '''
      Create/Replace resource.
      '''
      logger.debug('Creating/Updating resources<%s>: %s...'%(tipe, param['uri']))
      rep=self.put('/resources{0}?overwrite=true'.format(param['uri']), param)
      if 200<=rep.status_code<300:
         logger.debug('Creating/Updating resource<%s> successful.'%self.kwargs['path'])
      else:
         logger.warning('Creating/Updating resource<%s> unsuccessful with status-code: %s'%(self.kwargs['path'], rep.status_code))
         logger.debug(html.unescape(rep.text))
         logger.debug(param)
