# Generated by Django 3.2.6 on 2021-09-02 09:17

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
        ('webframe', '0021_numbering'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='webframe.models.ValueObject.id.helptext', primary_key=True, serialize=False, verbose_name='webframe.models.ValueObject.id')),
                ('lmd', models.DateTimeField(auto_now=True, help_text='webframe.models.ValueObject.lmd.helptext', verbose_name='webframe.models.ValueObject.lmd')),
                ('cd', models.DateTimeField(auto_now_add=True, help_text='webframe.models.ValueObject.cd.helptext', verbose_name='webframe.models.ValueObject.cd')),
                ('effDate', models.DateTimeField(default=django.utils.timezone.now, help_text='webframe.models.AliveObject.effDate.helptext', verbose_name='webframe.models.AliveObject.effDate')),
                ('expDate', models.DateTimeField(blank=True, help_text='webframe.models.AliveObject.expDate.helptext', null=True, verbose_name='webframe.models.AliveObject.expDate')),
                ('enabled', models.BooleanField(default=True, help_text='webframe.models.AliveObject.enabled.helptext', verbose_name='webframe.models.AliveObject.enabled')),
                ('sequence', models.FloatField(default=9223372036854775807, verbose_name='webframe.models.OrderableValueObject.sequence')),
                ('name', models.CharField(default='/', help_text='webframe.models.MenuItem.name.helptext', max_length=256, verbose_name='webframe.models.MenuItem.name')),
                ('icon', models.CharField(blank=True, help_text='webframe.models.MenuItem.icon.help', max_length=128, null=True, verbose_name='webframe.models.MenuItem.icon')),
                ('label', models.CharField(blank=True, help_text='webframe.models.MenuItem.label.helptext', max_length=1024, null=True, verbose_name='webframe.models.MenuItem.label')),
                ('image', models.ImageField(blank=True, help_text='webframe.models.MenuItem.image.helptext', null=True, upload_to=webframe.models.MenuItem.__getImageLocation__, verbose_name='webframe.models.MenuItem.image')),
                ('props', models.JSONField(blank=True, default={'class': None, 'style': None, 'target': None, 'title': None}, help_text='webframe.models.MenuItem.props.help', null=True, verbose_name='webframe.models.MenuItem.props')),
                ('onclick', models.TextField(default='window.location.href=this.data.props.href?this.data.props.href:"#";', help_text='webframe.models.MenuItem.onclick.helptext', max_length=2048, verbose_name='webframe.models.MenuItem.onclick')),
                ('mousein', models.TextField(blank=True, help_text='webframe.models.MenuItem.mousein.helptext', max_length=1024, null=True, verbose_name='webframe.models.MenuItem.mousein')),
                ('mouseout', models.TextField(blank=True, help_text='webframe.models.MenuItem.mouseout.helptext', max_length=1024, null=True, verbose_name='webframe.models.MenuItem.mouseout')),
                ('cb', models.ForeignKey(blank=True, default=webframe.CurrentUserMiddleware.get_current_user, help_text='webframe.models.ValueObject.cb.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='menuitem_cb', to=settings.AUTH_USER_MODEL, verbose_name='webframe.models.ValueObject.cb')),
                ('lmb', models.ForeignKey(blank=True, default=webframe.CurrentUserMiddleware.get_current_user, help_text='webframe.models.ValueObject.lmb.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='menuitem_lmb', to=settings.AUTH_USER_MODEL, verbose_name='webframe.models.ValueObject.lmb')),
                ('parent', models.ForeignKey(blank=True, help_text='webframe.models.MenuItem.parent.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, to='webframe.menuitem', verbose_name='webframe.models.MenuItem.parent')),
                ('user', models.ForeignKey(blank=True, help_text='webframe.models.MenuItem.user.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='webframe.models.MenuItem.user')),
            ],
            options={
                'verbose_name': 'webframe.models.MenuItem',
                'verbose_name_plural': 'webframe.models.MenuItems',
                'unique_together': {('parent', 'user', 'name')},
            },
            bases=(models.Model, webframe.models.Dictable),
        ),
    ]
