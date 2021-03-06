# Generated by Django 3.1.1 on 2020-10-01 09:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid
import webframe.CurrentUserMiddleware
import webframe.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('webframe', '0011_preference_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='Numbering',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='webframe.models.ValueObject.id.helptext', primary_key=True, serialize=False, verbose_name='webframe.models.ValueObject.id')),
                ('lmd', models.DateTimeField(auto_now=True, help_text='webframe.models.ValueObject.lmd.helptext', verbose_name='webframe.models.ValueObject.lmd')),
                ('cd', models.DateTimeField(auto_now_add=True, help_text='webframe.models.ValueObject.cd.helptext', verbose_name='webframe.models.ValueObject.cd')),
                ('effDate', models.DateTimeField(default=django.utils.timezone.now, help_text='webframe.models.AliveObject.effDate.helptext', verbose_name='webframe.models.AliveObject.effDate')),
                ('expDate', models.DateTimeField(blank=True, help_text='webframe.models.AliveObject.expDate.helptext', null=True, verbose_name='webframe.models.AliveObject.expDate')),
                ('enabled', models.BooleanField(default=True, help_text='webframe.models.AliveObject.enabled.helptext', verbose_name='webframe.models.AliveObject.enabled')),
                ('name', models.CharField(help_text='webframe.models.Numbering.name.helptxt', max_length=100, verbose_name='webframe.models.Numbering.name')),
                ('pattern', models.CharField(help_text='webframe.models.Numbering.pattern.helptxt', max_length=100, verbose_name='webframe.models.Numbering.pattern')),
                ('next_val', models.IntegerField(default=0, help_text='webframe.models.Numbering.next_val.helptxt', verbose_name='webframe.models.Numbering.next_val')),
                ('step_val', models.IntegerField(default=1, help_text='webframe.models.Numbering.step_val.helptxt', verbose_name='webframe.models.Numbering.step_val')),
                ('cb', models.ForeignKey(blank=True, default=webframe.CurrentUserMiddleware.get_current_user, help_text='webframe.models.ValueObject.cb.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='numbering_cb', to=settings.AUTH_USER_MODEL, verbose_name='webframe.models.ValueObject.cb')),
                ('lmb', models.ForeignKey(blank=True, default=webframe.CurrentUserMiddleware.get_current_user, help_text='webframe.models.ValueObject.lmb.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='numbering_lmb', to=settings.AUTH_USER_MODEL, verbose_name='webframe.models.ValueObject.lmb')),
            ],
            options={
                'verbose_name': 'webframe.models.Numbering', 
                'verbose_name_plural': 'webframe.models.Numberings',
                'permissions': [('exec_numbering', 'Can execute the number')],
            },
            bases=(models.Model, webframe.models.Dictable),
        ),
    ]
