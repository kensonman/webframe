# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-10-10 12:41
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc
import uuid
import webframe.CurrentUserMiddleware


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('webframe', '0002_preferences'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='preference',
            name='enabled',
        ),
        migrations.AddField(
            model_name='preference',
            name='cb',
            field=models.ForeignKey(blank=True, default=webframe.CurrentUserMiddleware.get_current_user, help_text='ValueObject.cb.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='preference_cb', to=settings.AUTH_USER_MODEL, verbose_name='ValueObject.cb'),
        ),
        migrations.AddField(
            model_name='preference',
            name='cd',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 10, 10, 12, 41, 25, 359174, tzinfo=utc), help_text='ValueObject.cd.helptext', verbose_name='ValueObject.cd'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='preference',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, help_text='ValueObject.id.helptext', primary_key=True, serialize=False, verbose_name='ValueObject.id'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='lmb',
            field=models.ForeignKey(blank=True, default=webframe.CurrentUserMiddleware.get_current_user, help_text='ValueObject.lmb.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='preference_lmb', to=settings.AUTH_USER_MODEL, verbose_name='ValueObject.lmb'),
        ),
    ]