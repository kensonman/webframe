# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-13 03:47
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid
import webframe.CurrentUserMiddleware


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('webframe', '0003_ValueObjectAndAliveObject'),
    ]

    operations = [
        migrations.CreateModel(
            name='GrantedPrivilege',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.UUIDField(verbose_name='webframe.models.GrantedPrivilege.item')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='webframe.models.GrantedPrivilege.owner')),
            ],
            options={
                'verbose_name_plural': 'webframe.models.GrantedPrivilege',
                'verbose_name': 'webframe.models.GrantedPrivilege',
            },
        ),
        migrations.CreateModel(
            name='Privilege',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='webframe.models.Privilege.name')),
                ('desc', models.TextField(blank=True, max_length=200, null=True, verbose_name='webframe.models.Privilege.desc')),
                ('contenttype', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name_plural': 'webframe.models.Privileges',
                'verbose_name': 'webframe.models.Privilege',
            },
        ),
        migrations.AlterField(
            model_name='preference',
            name='cb',
            field=models.ForeignKey(blank=True, default=webframe.CurrentUserMiddleware.get_current_user, help_text='webframe.models.ValueObject.cb.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='preference_cb', to=settings.AUTH_USER_MODEL, verbose_name='webframe.models.ValueObject.cb'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='cd',
            field=models.DateTimeField(auto_now_add=True, help_text='webframe.models.ValueObject.cd.helptext', verbose_name='webframe.models.ValueObject.cd'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, help_text='webframe.models.ValueObject.id.helptext', primary_key=True, serialize=False, verbose_name='webframe.models.ValueObject.id'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='lmb',
            field=models.ForeignKey(blank=True, default=webframe.CurrentUserMiddleware.get_current_user, help_text='webframe.models.ValueObject.lmb.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='preference_lmb', to=settings.AUTH_USER_MODEL, verbose_name='webframe.models.ValueObject.lmb'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='lmd',
            field=models.DateTimeField(auto_now=True, help_text='webframe.models.ValueObject.lmd.helptext', verbose_name='webframe.models.ValueObject.lmd'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='name',
            field=models.CharField(help_text='webframe.models.Preference.name.helptext', max_length=100, verbose_name='webframe.models.Preference.name'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='owner',
            field=models.ForeignKey(blank=True, help_text='webframe.models.Preference.owner.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='preference_owner', to=settings.AUTH_USER_MODEL, verbose_name='Pwebframe.models.reference.owner'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='parent',
            field=models.ForeignKey(blank=True, help_text='webframe.models.Preference.parent.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, to='webframe.Preference', verbose_name='webframe.models.Preference.parent'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='sequence',
            field=models.FloatField(default=0.5, help_text='webframe.models.Preference.sequence.helptext', verbose_name='webframe.models.Preference.sequence'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='value',
            field=models.CharField(help_text='webframe.models.Preference.value.helptext', max_length=1024, verbose_name='webframe.models.Preference.value'),
        ),
        migrations.AddField(
            model_name='grantedprivilege',
            name='privilege',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webframe.Privilege', verbose_name='webframe.models.GrantedPrivilege.privilege'),
        ),
    ]
