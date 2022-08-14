# -*- coding: utf-8 -*-
# File:     /src/webframe/tasks.py
# Author:   Kenson Man <kenson@kenson.idv.hk>
# Date:     2021-11-10 13:09
# Desc:     Define the tasks for webframe Projects
from celery import shared_task 
from datetime import datetime
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, User
from django.db import transaction
from html import escape as escapeHtml
from webframe.functions import getBool, LogMessage as log
from webframe.models import Preference
import logging, time, re, uuid, json

logger=logging.getLogger('webframe.tasks')

@shared_task(bind=True)
def sendEmail( *args, **kwargs ):
   '''
   Sending the email asynchronously. It will sending the email according to settings.

   You can use the [SendGrid API](https://github.com/sendgrid/sendgrid-python) or [SMTP settings](https://docs.djangoproject.com/en/3.2/topics/email/). If
   sending via SendGrid API, the [EMAIL_HOST_PASSWORD](https://docs.djangoproject.com/en/3.2/ref/settings/#std:setting-EMAIL_HOST_PASSWORD) is used for api-key.

   Parameters are as follow:
      +--------------------+--------------------+--------------------+
      | NAME               | TYPE               | REMARKS            |
      +--------------------+--------------------+--------------------+
      | subject            | string             | The subject of the email. 
      | sender             | string             | The sender of the email.
      | reply_to           | string             | A list or tuple of recipient addresses used in the “Reply-To” header when sending the email.
      | recipients         | string or list     | Comma delimited recipient email address.
      | cc                 | string or list     | Comma delimited cc email address.
      | bcc                | string or list     | Comma delimited bcc email address.
      | content            | string             | HTML base email content.
      | plain              | string             | TEXT base email content. If not specified, the HTML base content will be applied (removed all html tags).
      | attachments        | list               | A list of attachments to put on the message. These can be either MIMEBase instances, or (filename, content, mimetype) triples.
      +--------------------+--------------------+--------------------+
   '''
   if 'subject' not in kwargs: raise ValueError('\"subject\" is required')
   if 'sender' not in kwargs: raise ValueError('\"sender\" is required')
   if 'content' not in kwargs: raise ValueError('\"content\" is required')

   taskId=kwargs.get('task_id', 'this')
   logger=logging.getLogger('webframe.tasks.sendEmail')
   logger.debug('Sending email with params...{0}'.format(json.dumps(kwargs)))
   try:
      subject=kwargs.get('subject', 'NoSubject').format(**kwargs)
      sender=kwargs.get('sender', 'kenson@kenson.idv.hk')
      split=lambda s: re.findall(r'[^,;\s]+', s) if isinstance(s, str) else s #The split method for spliting email addresses
      recipients=split(kwargs.get('recipients', ''))
      cc=split(kwargs.get('cc', ''))
      bcc=split(kwargs.get('bcc', ''))
      if not ( recipients or cc or bcc ): raise ValueError('Either \"recipients\", \"cc\", or \"bcc\" is required')
      if not ( hasattr(recipients, '__iter__') and hasattr(cc, '__iter__') and hasattr(bcc, '__iter__') ): raise ValueError('\"recipients\", \"cc\", or \"bcc" cannot convert to a list')
      html=kwargs.get('content', 'The simple email').format(**kwargs)
      txt=re.sub(re.compile(r'<.*?>'), '', html)
      txt=kwargs.get('plain', txt)

      if getBool(getattr(settings, 'EMAIL_SENDGRID', False)):
          logger.debug('Sending via sendgrid!')
          from sendgrid import SendGridAPIClient
          from sendgrid.helpers.mail import Mail, From, To, Cc, Bcc
          logger.debug('   apikey: {0}'.format(settings.EMAIL_HOST_PASSWORD))
          sg = SendGridAPIClient(settings.EMAIL_HOST_PASSWORD)
          recipients=[To(r, r) for r in recipients]
          for rec in recipients:
            msg=Mail(from_email=sender, to_emails=recipients, subject=subject, html_content=html, plain_text_content=txt)
            if cc: msg.cc=[Cc(r, r) for r in cc]
            if bcc: msg.bcc=[Bcc(r, r) for r in bcc]
            rep=sg.send(msg)
            logger.debug('SG-status-code: {0}'.format(rep.status_code))
            logger.debug('SG-body: {0}'.format(rep.body))
            logger.debug('SG-headers: {0}'.format(rep.headers))
      else:
          logger.debug('Sending via SMTP!')
          from django.core.mail import EmailMultiAlternatives
          logger.info(log('Sending email with task number: {0}', taskId))
          msg=EmailMultiAlternatives(subject, txt, sender, recipients, cc, bcc)
          if 'reply_to' in kwargs: msg.reply_to=kwargs['reply_to']
          if 'attachments' in kwargs: msg.attachments=kwargs['attachments']
          msg.attach_alternative(html, 'text/html')
          logger.debug(log('   with {0}', {'subject':subject, 'sender':sender, 'recipients':recipients, 'cc':cc, 'bcc':bcc, 'content':html, 'text':txt}))
          msg.send()
          logger.debug(log('   Sent email. {0}', taskId))
   except:
      logger.exception('Cannot send the email properly')
      raise
