from django.test import Client
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
import logging
from django.conf import settings
import logging, sys, os

logger=logging.getLogger('test.health')

class HeaderApiTest(TestCase):
   def setUp(self):
      logger.info('Setting up the authentication...')
      from django.contrib.auth.models import User
      self.super=User(username='super', is_superuser=True, is_staff=True, is_active=True)
      self.super.set_password('superpass')
      self.super.save()
      logger.debug('>   Created superuser: {0}'.format(self.super.username))
      self.super.token=Token.objects.create(user=self.super)
      logger.debug('>   Created token for {0}: {1}'.format(self.super.username, self.super.token.key))

      self.normal=User(username='normal', is_active=True)
      self.normal.set_password('normalperpass')
      self.normal.save()
      logger.debug('>   Created normaluser: {0}'.format(self.normal.username))
      self.normal.token=Token.objects.create(user=self.normal)
      logger.debug('>   Created token for {0}: {1}'.format(self.normal.username, self.normal.token.key))

   def test_generatedNavBar(self):
      url=reverse('webframe:headers')
      client=Client()
      logger.info('Running index url without authentication: {0}...'.format(url))
      rep=client.get(url, follow=True)
      logger.debug('response code: {0}'.format(rep.status_code))
      self.assertTrue(200 <= rep.status_code < 300)
      self.assertEquals(rep.json()['name'], 'Generated NavBar')

      user=self.super
      client=Client(HTTP_AUTHORIZATION='Token {0}'.format(user.token))
      logger.info('Running index url with authentication({1}): {0}...'.format(url, user.username))
      rep=client.get(url, follow=True)
      logger.debug('response code: {0}'.format(rep.status_code))
      self.assertTrue(200 <= rep.status_code < 300)
      self.assertEquals(rep.json()['name'], 'Generated NavBar')
      self.assertTrue(str(rep.content).index(reverse('admin:index'))>=0)

      user=self.normal
      client=Client(HTTP_AUTHORIZATION='Token {0}'.format(user.token))
      logger.info('Running index url with authentication({1}): {0}...'.format(url, user.username))
      rep=client.get(url, follow=True)
      logger.debug('response code: {0}'.format(rep.status_code))
      self.assertTrue(200 <= rep.status_code < 300)
      self.assertEquals(rep.json()['name'], 'Generated NavBar')
      try:
         rep.content.decode('ascii').index(reverse('admin:index'))
         self.fail('Found the admin-url')
      except:
         pass

class FunctionsTestCase(TestCase):
   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.logger=logging.getLogger('test.{0}'.format(self.__class__.__name__))
      self.logger.setLevel(os.environ.get('LOG_LEVEL', logging.DEBUG))

   def setUp(self):
      import os
      keyfile=getattr(settings, 'SECRET_KEY_FILE', 'secret.key')
      if not os.path.isabs(keyfile): keyfile=os.path.join(os.path.dirname(__file__), keyfile)
      if os.path.isfile(keyfile): 
         self.logger.info('Backing up the secret file: {0} => {1}'.format(keyfile, '%s__'%keyfile))
         os.rename(keyfile, '%s__'%keyfile)

   def tearDown(self):
      import os
      keyfile=getattr(settings, 'SECRET_KEY_FILE', 'secret.key')
      if not os.path.isabs(keyfile): keyfile=os.path.join(os.path.dirname(__file__), keyfile)
      if os.path.isfile(keyfile): 
         self.logger.info('Purging the testing secret key: {0}'.format(keyfile))
         os.remove(keyfile)
      keyfile='%s__'%keyfile
      if os.path.isfile(keyfile): 
         self.logger.info('Restore the secret file: {0} => {1}'.format('%s__'%keyfile, keyfile))
         os.rename(keyfile, keyfile[:-2])

   def test_getSecretKeyFromPassword(self):
      self.logger.warning('test_getSecretKeyFromPassword')
      from webframe.functions import getSecretKeyFromPassword

      self.assertEquals(getSecretKeyFromPassword('abc'), getSecretKeyFromPassword('abc'))
      self.assertNotEquals(getSecretKeyFromPassword('abc'), getSecretKeyFromPassword('abcd'))

   def test_getRandomPassword(self):
      self.logger.warning('test_getRandomPassword')
      from webframe.functions import getRandomPassword as pwd
      self.assertEquals(len(pwd()), 128)
      self.assertEquals(len(pwd(30)), 30)
      self.logger.info('One of the randome password: {0}'.format(pwd()))

   def test_getSecretKey(self):
      self.logger.warning('test_getSecretKey')
      from webframe.functions import getSecretKey
      import os

      keyfile=getattr(settings, 'SECRET_KEY_FILE', 'secret.key')
      if not os.path.isabs(keyfile): keyfile=os.path.join(os.path.dirname(__file__), keyfile)
      self.assertTrue(not os.path.isfile(keyfile))
      self.logger.warning('The random password: {0}'.format(getSecretKey()))
      self.assertTrue(os.path.isfile(keyfile))

   def test_encryption(self):
      self.logger.warning('test_encryption')
      from webframe.functions import encrypt, decrypt, getRandomPassword

      pwd=getRandomPassword()
      src='This is the source data.'
      self.logger.warning('The source data: {0}'.format(src))
      self.logger.warning('The random password: {0}'.format(pwd))
      enc=encrypt(src, pwd)
      self.logger.warning('The encrypted data: {0}'.format(enc))
      self.assertNotEquals(src, enc)
      dec=decrypt(enc, pwd)
      self.logger.warning('The decrypted data: {0}'.format(dec))
      self.assertEquals(src, dec)
      try:
         decrypt(enc, 'wrong password')
         self.fail('Wrong password should get the error instead')
      except ValueError:
         pass
