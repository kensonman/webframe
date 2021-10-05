from django.test import Client
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
import logging

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
      rep=client.get(url)
      logger.debug('response code: {0}'.format(rep.status_code))
      self.assertTrue(200 <= rep.status_code < 300)
      self.assertEquals(rep.json()['name'], 'Generated NavBar')

      user=self.super
      client=Client(HTTP_AUTHORIZATION='Token {0}'.format(user.token))
      logger.info('Running index url with authentication({1}): {0}...'.format(url, user.username))
      rep=client.get(url)
      logger.debug('response code: {0}'.format(rep.status_code))
      self.assertTrue(200 <= rep.status_code < 300)
      self.assertEquals(rep.json()['name'], 'Generated NavBar')
      self.assertTrue(str(rep.content).index(reverse('admin:index'))>=0)

      user=self.normal
      client=Client(HTTP_AUTHORIZATION='Token {0}'.format(user.token))
      logger.info('Running index url with authentication({1}): {0}...'.format(url, user.username))
      rep=client.get(url)
      logger.debug('response code: {0}'.format(rep.status_code))
      self.assertTrue(200 <= rep.status_code < 300)
      self.assertEquals(rep.json()['name'], 'Generated NavBar')
      try:
         rep.content.decode('ascii').index(reverse('admin:index'))
         self.fail('Found the admin-url')
      except ValueError:
         pass
