# -*- coding: utf-8 -*-
# 
# File: src/webframe/management/commands/deployreports.py
# Date: 2019-12-13 20:50
# Author: Kenson Man <kenson@kenson.idv.hk>
# Desc: Install the report into JasperServer
# 
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
import logging, requests, json, base64, html, glob, os


logger=logging.getLogger('webframe.commands.install')
try:
   import xml.etree.cElementTree as ET
except ImportError:
   logger.warning('Using the Python ElementTree instead of CElementTree')
   import xml.etree.ElementTree as ET
b64=lambda path: base64.b64encode(Path(path).read_text().encode('utf-8')).decode('ascii')
ns='http://jasperreports.sourceforge.net/jasperreports'

class Command(BaseCommand):
   help     = 'Install and prepare the reports into JasperServer'

   def add_arguments(self, parser):
      parser.add_argument('--host', dest='rpthost', type=str, help='The hostname of the report server; Default: http://rpthost:8080', default='http://rpthost:8080')
      parser.add_argument('--admin', dest='adminuser', type=str, help='The admin username of the report server; Default: jasperadmin', default='jasperadmin')
      parser.add_argument('--pass', dest='adminpass', type=str, help='The admin password of the report server; Default: jasperadmin', default='jasperadmin')
      parser.add_argument('--prefix', dest='prefix', type=str, help='The prefix of installed reports URI; Default: /webframe', default='/webframe/')
      parser.add_argument('--reports', dest='reports', type=str, help='The path of the target report(s); Default: ./rpt/MyReports/*xml', default='./rpt/MyReports/*.jrxml')
      parser.add_argument('--dbconn', dest='dbconn', type=str, help='Specify the database connection for each imported report; Default: ./rpt/MyReports/DBConn.xml', default='./rpt/MyReports/DBConn.xml')
      parser.add_argument('--role', dest='role', type=str, help='The role to access the sitesys report repository', default='sitesys')

   def jasperserver(self, url, **kwargs):
      ''' Communicate/Query the JasperServer '''
      myargs=self.kwargs.copy()
      myargs.update(kwargs)
      data=dict() if 'data' not in myargs else json.dumps(myargs['data']).encode('utf-8')
      auth=(myargs['adminuser'], myargs['adminpass'])
      headers={'Content-Type': myargs.get('contentType', 'application/json')}
      if 'headers' in kwargs: headers.update(kwargs['headers'])
      url=url.format(**myargs)
      method=myargs.get('method','put').upper()

      if method=='PUT':
         logger.debug('Putting resources<{0}>: {1}'.format(kwargs['contentType'], url))
         rep=requests.put(url, auth=auth, data=data, headers=headers)
      elif method=='POST':
         logger.debug('Posting resources<{0}>: {1}'.format(kwargs['contentType'], url))
         rep=requests.post(url, auth=auth, data=data, headers=headers)
      elif method=='GET':
         logger.debug('Getting resources<{0}>: {1}'.format(kwargs['contentType'], url))
         rep=requests.get(url, auth=auth, data=data, headers=headers)
      elif method=='DELETE':
         logger.debug('Deleting resources<{0}>: {1}'.format(kwargs['contentType'], url))
         rep=requests.delete(url, auth=auth, data=data, headers=headers)
      else:
         raise TypeError('Unknow HTTP method: {0}'.format(method))
      return rep

   def init_role(self):
      # Checking the role are existing
      url='{rpthost}/rest_v2/roles/{role}'
      rep=self.jasperserver(url, contentType='role', method='get')
      if rep.status_code != 200:
         #If NOT exists
         logger.info('Creating reporting role: %s ...'%self.kwargs['role'])
         rep=self.jasperserver(url, data={}, contentType='role', method='put')
         if 200<=rep.status_code<300:
            logger.info('Role<%s> has been created successfully!'%self.kwargs['role'])
         else:
            logger.warning('Role<%s> cannot been created, status-code: %s'%(self.kwargs['role'], rep.status_code))
            logger.debug(rep.text)

   def init_user(self):
      # Make sure the user is created.
      user=settings.REPORTING['username']
      pawd=settings.REPORTING['password']
      url='{rpthost}/rest_v2/users/{user}'
      rep=self.jasperserver(url, contentType='user', method='get', user=user)
      if rep.status_code!=200:
         logger.info('Creating/Updating report user: %s ...'%settings.REPORTING['username'])
         rep=self.jasperserver(url, contentType='user', method='put', user=user, data={'fullName': 'Deploy by script', 'enabled': True, 'password': pawd, 'rules': [{'name': 'ROLE_USER'}, {'name': self.kwargs['role']}]})
         if 200<=rep.status_code<300:
            logger.info('Role<%s> has been created successfully!'%self.kwargs['role'])
         else:
            logger.warning('Role<%s> cannot been created, status-code: %s'%(self.kwargs['role'], rep.status_code))
            logger.debug(rep.text)

   def import_report(self, filename, root):
      #Import the jasper report (*.jrxml)
      types=dict()
      def gettype(rptname, types, tipe):
         if tipe not in types:
            uri='{rpthost}/rest_v2/resources{prefix}{rptname}_Data/{tipe}'
            contentType='application/repository.dataType+json'
            rep=self.jasperserver(uri, method='get', contentType=contentType, tipe=tipe, rptname=rptname, headers={'accept': 'application/json'})
            if 200 <= rep.status_code < 300:
               types[tipe]=rep.json()['uri']
            else:
               logger.debug('      Creating contentType for {0}'.format(tipe))
               #Server support type: text|number|date|dateTime|time
               if tipe in ['java.lang.Double', 'java.lang.Float', 'java.lang.Integer', 'java.lang.Long', 'java.lang.Short', 'java.math.BigDecimal']:
                  serverType='number'
               elif tipe=='java.sql.Date':
                  serverType='date'
               elif tipe=='java.sql.Time':
                  serverType='time'
               elif tipe=='java.sql.Timestamp' or tipe=='java.util.Date':
                  serverType='datetime'
               else:
                  serverType='text'
               rep=self.jasperserver(uri, method='put', contentType=contentType, tipe=tipe, rptname=rptname, data={
                  'label': tipe, 
                  'description': 'Data-Type for {0}'.format(tipe),
                  'permissionMask': '0', 
                  'version': '1', 
                  'type': serverType,
                  'strictMax': 'false', 
                  'strictMin': 'false', 
               })
               if 200 <= rep.status_code < 300:
                  logger.info('      Created/Updated data-type for {0}: {1}...'.format(rptname, tipe))
                  url=rep.url
                  url=url[url.index('rest_v2/resources')+17:]
                  types[tipe]=url
               else:
                  logger.debug('      [{0}]: {1}'.format(rep.status_code, rep.text))
                  raise TypeError('Cannot create the data-type for report: {0}'.format(rptname))
         return types[tipe]

      def property(rptname, tag):
         logger.debug('   Handling parameter<{0}> as {1}'.format(tag.attrib['name'], tag.attrib['class']))
         tipe=gettype(rptname, types, tag.attrib['class'])
         uri='{rpthost}/rest_v2/resources{prefix}{rptname}_Data/InputControl.{name}'
         contentType='application/repository.inputControl+json'
         rep=self.jasperserver(uri, method='get', contentType=contentType, name=tag.attrib['name'], rptname=rptname, headers={'accept': 'application/json'})
         if 200 <= rep.status_code < 300:
            return rep.json()['uri']
         else:
            desc=tag.find('{{{0}}}parameterDescription'.format(ns))
            rep=self.jasperserver(uri, contentType=contentType, name=tag.attrib['name'], rptname=rptname, data={
               'label': 'InputControl.{0}'.format(tag.attrib['name']),
               'description': None if not desc else desc.text,
               'permissionMask': '0',
               'version': '1',
               'mandatory': True,
               'type': '2', #2==Single Value
               'dataType': {'dataTypeReference': {'uri': tipe}},
               'usedFields': tag.attrib['name'],
               'verbise': True,
            })
            if 200 <= rep.status_code < 300:
               logger.info('   Created/Updated parameter<{0}> for report<{1}>...'.format(tag.attrib['name'], rptname))
               return rep.url[rep.url.index('rest_v2/resources')+17:]
            else:
               logger.debug('   [{0}]: {1}'.format(rep.status_code, rep.text))
               raise TypeError('Cannot create the parameter<{0}> for report<{1}>'.format(tag.attrib['name'], rptname))

      def subreport(cwd, rptname, tag):
         path=tag.find('{{{0}}}subreportExpression'.format(ns)).text
         path=path[path.index('\"')+1:]
         path='{0}.jrxml'.format(path[0:path.index('\"')])
         filename=os.path.join(cwd, path)
         sr=ET.ElementTree(file=filename).getroot()
         logger.debug('   Handling subreport<{0}>: {1}...'.format(sr.attrib['name'], filename))
         uri='{rpthost}/rest_v2/resources{prefix}{path}'.format(rpthost=self.kwargs['rpthost'], prefix=self.kwargs['prefix'], path=path) 
         desc=sr.find('{{{0}}}property[@name=\'com.jaspersoft.studio.report.description\']'.format(ns))
         rep=self.jasperserver(uri, contentType='application/repository.file+json', method='get', headers={'accept': 'application/json'})
         if 200 <= rep.status_code < 300:
            pass
         else:
            rep=self.jasperserver(uri, contentType='application/repository.file+json', method='put', data={
               'label': sr.attrib['name'],
               'description': None if not desc else desc,
               'permissionMask': '0',
               'version': '1',
               'type': 'jrxml',
               'content': b64(filename),
            })
            if 200 <= rep.status_code < 300:
               logger.info('      Created/Updated subreport<{0}>...'.format(sr.attrib['name']))
            else:
               logger.debug('      [{0}]: {1}'.format(rep.status_code, rep.text))
               raise TypeError('Cannot create the subreport<{0}>...'.format(sr.attrib['name']))

      name=root.attrib['name'].replace('-', '_')
      logger.info('Importing "{1}" JRXML: {0}...'.format(filename, name))
      cwd=os.path.dirname(filename)
      parameters=dict()
      for p in root.findall('{{{0}}}parameter'.format(ns)):
         parameters[p.attrib['name']]=property(name, p)

      for r in root.iter('{{{0}}}subreport'.format(ns)):
         subreport(cwd, name, r)

      uri='{rpthost}/rest_v2/resources{prefix}{name}'
      rep=self.jasperserver(uri, contentType='application/repository.reportUnit+json', method='get', name=name, headers={'accept': 'application/json'})
      if not 200 <= rep.status_code < 300:
         desc=root.find('{{{0}}}property[@name=\'com.jaspersoft.studio.report.description\']'.format(ns))
         rep=self.jasperserver(uri, contentType='application/repository.reportUnit+json', method='put', name=name, data={
            'label': root.attrib['name'],
            'description': None if not desc else desc,
            'permissionMask': '0',
            'version': '1',
            'controlsLayout': 'popupScreen',
            'alwaysPromptControls': 'true',
            'dataSource': {'dataSourceReference': {'uri': self.dbconn}},
            'inputControls': [{'inputControlReference': {'uri': parameters[p]}} for p in parameters],
            'jrxml': {
               'jrxmlFile': {
                  'type': 'jrxml',
                  'label': 'jrxml',
                  'content': b64(filename)
               }
            }
         })
         if 200 <= rep.status_code < 300:
            logger.info('      Created/Updated report<{0}>...'.format(name))
         else:
            logger.debug('      [{0}]: {1}'.format(rep.status_code, rep.text))
            raise TypeError('Cannot create the report<{0}>...'.format(name))

   def import_file(self, filename):
      # Import the xml file
      logger.debug('Importing file: {0}'.format(filename))
      root=ET.ElementTree(file=filename).getroot()
      if root.tag=='jdbcDataAdapter':
         #Importing the jdbc
         self.import_ds(root)
      elif root.tag=='{{{0}}}jasperReport'.format(ns):
         #Importing the JasperReport
         self.import_report(filename, root)
      else:
         logger.info('Unknow ROOT Tag in the xml, skipping...')

   def import_ds(self, root):
      # Make sure the data-source created
      url='{rpthost}/rest_v2/resources{prefix}'
      contentType='application/repository.jdbcDataSource+json'
      name=root.find('name').text
      rep=self.jasperserver(url, name=name, contentType=contentType, method='get')
      if rep.status_code==200:
         self.jasperserver(url, name=name, contentType=contentType, method='delete')
      rep=self.jasperserver(url, name=name, contentType=contentType, method='post', data={
         'label': name,
         'description': 'The database connection imported by deployreports.py',
         'permissionMask': '0',
         'version': '1',

         'driverClass': root.find('driver').text,
         'username': settings.REPORTING['username'], #Refer to rpt/createUser.sql
         'password': settings.REPORTING['password'], #Refer to rpt/createUser.sql
         'connectionUrl': root.find('url').text,
      })
      if 200 <= rep.status_code < 300:
         logger.info('Create/Update datatsource<{0}> successfully.'.format(name))
         self.dbconn='{prefix}{name}'.format(prefix=self.kwargs['prefix'], name=name)
      else:
         logger.warning('Create/Update datasource<{0}> failed with status code {1}'.format(name, rep.status_code))
         logger.warning(rep.text)

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

      logger.info('Report server are located at "{host}" with admin-user: {user}'.format(host=self.kwargs['rpthost'], user=kwargs['adminuser']))
      self.init_role()
      self.init_user()
      self.import_file(self.kwargs['dbconn'])
      for f in glob.glob(self.kwargs['reports']):
         self.import_file(f)
