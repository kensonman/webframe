# Generated by Django 3.2.6 on 2021-09-15 08:08

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
        ('webframe', '0022_menuitem'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='menuitem',
            options={'verbose_name': 'MenuItem', 'verbose_name_plural': 'MenuItems'},
        ),
        migrations.AlterModelOptions(
            name='numbering',
            options={'permissions': [('exec_numbering', 'Can execute the number')], 'verbose_name': 'Numbering', 'verbose_name_plural': 'Numberings'},
        ),
        migrations.AlterModelOptions(
            name='profile',
            options={'verbose_name': 'Profile', 'verbose_name_plural': 'Profiles'},
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='cb',
            field=models.ForeignKey(blank=True, default=webframe.CurrentUserMiddleware.get_current_user, help_text='ValueObject.cb.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='menuitem_cb', to=settings.AUTH_USER_MODEL, verbose_name='ValueObject.cb'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='cd',
            field=models.DateTimeField(auto_now_add=True, help_text='ValueObject.cd.helptext', verbose_name='ValueObject.cd'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='effDate',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='AliveObject.effDate.helptext', verbose_name='AliveObject.effDate'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='enabled',
            field=models.BooleanField(default=True, help_text='AliveObject.enabled.helptext', verbose_name='AliveObject.enabled'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='expDate',
            field=models.DateTimeField(blank=True, help_text='AliveObject.expDate.helptext', null=True, verbose_name='AliveObject.expDate'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='icon',
            field=models.CharField(blank=True, help_text='MenuItem.icon.help', max_length=128, null=True, verbose_name='MenuItem.icon'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, help_text='ValueObject.id.helptext', primary_key=True, serialize=False, verbose_name='ValueObject.id'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='image',
            field=models.ImageField(blank=True, help_text='MenuItem.image.helptext', null=True, upload_to=webframe.models.MenuItem.__getImageLocation__, verbose_name='MenuItem.image'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='label',
            field=models.CharField(blank=True, help_text='MenuItem.label.helptext', max_length=1024, null=True, verbose_name='MenuItem.label'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='lmb',
            field=models.ForeignKey(blank=True, default=webframe.CurrentUserMiddleware.get_current_user, help_text='ValueObject.lmb.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='menuitem_lmb', to=settings.AUTH_USER_MODEL, verbose_name='ValueObject.lmb'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='lmd',
            field=models.DateTimeField(auto_now=True, help_text='ValueObject.lmd.helptext', verbose_name='ValueObject.lmd'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='mousein',
            field=models.TextField(blank=True, help_text='MenuItem.mousein.helptext', max_length=1024, null=True, verbose_name='MenuItem.mousein'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='mouseout',
            field=models.TextField(blank=True, help_text='MenuItem.mouseout.helptext', max_length=1024, null=True, verbose_name='MenuItem.mouseout'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='name',
            field=models.CharField(default='/', help_text='MenuItem.name.helptext', max_length=256, verbose_name='MenuItem.name'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='onclick',
            field=models.TextField(default='window.location.href=this.data.props.href?this.data.props.href:"#";', help_text='MenuItem.onclick.helptext', max_length=2048, verbose_name='MenuItem.onclick'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='parent',
            field=models.ForeignKey(blank=True, help_text='MenuItem.parent.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, to='webframe.menuitem', verbose_name='MenuItem.parent'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='props',
            field=models.JSONField(blank=True, default={'class': None, 'style': None, 'target': None, 'title': None}, help_text='MenuItem.props.help', null=True, verbose_name='MenuItem.props'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='sequence',
            field=models.FloatField(default=9223372036854775807, verbose_name='OrderableValueObject.sequence'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='user',
            field=models.ForeignKey(blank=True, help_text='MenuItem.user.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='MenuItem.user'),
        ),
        migrations.AlterField(
            model_name='numbering',
            name='cb',
            field=models.ForeignKey(blank=True, default=webframe.CurrentUserMiddleware.get_current_user, help_text='ValueObject.cb.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='numbering_cb', to=settings.AUTH_USER_MODEL, verbose_name='ValueObject.cb'),
        ),
        migrations.AlterField(
            model_name='numbering',
            name='cd',
            field=models.DateTimeField(auto_now_add=True, help_text='ValueObject.cd.helptext', verbose_name='ValueObject.cd'),
        ),
        migrations.AlterField(
            model_name='numbering',
            name='desc',
            field=models.CharField(blank=True, help_text='Numbering.desc.helptext', max_length=1024, null=True, verbose_name='Numbering.desc'),
        ),
        migrations.AlterField(
            model_name='numbering',
            name='effDate',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='AliveObject.effDate.helptext', verbose_name='AliveObject.effDate'),
        ),
        migrations.AlterField(
            model_name='numbering',
            name='enabled',
            field=models.BooleanField(default=True, help_text='AliveObject.enabled.helptext', verbose_name='AliveObject.enabled'),
        ),
        migrations.AlterField(
            model_name='numbering',
            name='expDate',
            field=models.DateTimeField(blank=True, help_text='AliveObject.expDate.helptext', null=True, verbose_name='AliveObject.expDate'),
        ),
        migrations.AlterField(
            model_name='numbering',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, help_text='ValueObject.id.helptext', primary_key=True, serialize=False, verbose_name='ValueObject.id'),
        ),
        migrations.AlterField(
            model_name='numbering',
            name='lmb',
            field=models.ForeignKey(blank=True, default=webframe.CurrentUserMiddleware.get_current_user, help_text='ValueObject.lmb.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='numbering_lmb', to=settings.AUTH_USER_MODEL, verbose_name='ValueObject.lmb'),
        ),
        migrations.AlterField(
            model_name='numbering',
            name='lmd',
            field=models.DateTimeField(auto_now=True, help_text='ValueObject.lmd.helptext', verbose_name='ValueObject.lmd'),
        ),
        migrations.AlterField(
            model_name='numbering',
            name='name',
            field=models.CharField(help_text='Numbering.name.helptxt', max_length=100, unique=True, verbose_name='Numbering.name'),
        ),
        migrations.AlterField(
            model_name='numbering',
            name='next_val',
            field=models.IntegerField(default=0, help_text='Numbering.next_val.helptxt', verbose_name='Numbering.next_val'),
        ),
        migrations.AlterField(
            model_name='numbering',
            name='pattern',
            field=models.CharField(default='{next}', help_text='Numbering.pattern.helptxt', max_length=100, verbose_name='Numbering.pattern'),
        ),
        migrations.AlterField(
            model_name='numbering',
            name='step_val',
            field=models.IntegerField(default=1, help_text='Numbering.step_val.helptxt', verbose_name='Numbering.step_val'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='_tipe',
            field=models.IntegerField(choices=[(0, 'Preference.TYPE.NONE'), (1, 'Preference.TYPE.INT'), (2, 'Preference.TYPE.DECIMAL'), (3, 'Preference.TYPE.BOOLEAN'), (4, 'Preference.TYPE.TEXT'), (5, 'Preference.TYPE.RICHTEXT'), (6, 'Preference.TYPE.URL'), (7, 'Preference.TYPE.EMAIL'), (8, 'Preference.TYPE.DATE'), (9, 'Preference.TYPE.TIME'), (10, 'Preference.TYPE.DATETIME'), (11, 'Preference.TYPE.UUIDS'), (12, 'Preference.TYPE.LIST'), (13, 'Preference.TYPE.JSON'), (14, 'Preference.TYPE.FILEPATH')], default=4, help_text='Preference.tipe.helptext', verbose_name='Preference.tipe'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='_value',
            field=models.TextField(blank=True, help_text='Preference.value.helptext', max_length=4096, null=True, verbose_name='Preference.value'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='cb',
            field=models.ForeignKey(blank=True, default=webframe.CurrentUserMiddleware.get_current_user, help_text='ValueObject.cb.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='preference_cb', to=settings.AUTH_USER_MODEL, verbose_name='ValueObject.cb'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='cd',
            field=models.DateTimeField(auto_now_add=True, help_text='ValueObject.cd.helptext', verbose_name='ValueObject.cd'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='encrypted',
            field=models.BooleanField(default=False, help_text='Preference.encrypted.helptxt', verbose_name='Preference.encrypted'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='filecontent',
            field=models.FileField(blank=True, help_text='Preference.filecontent.helptext', max_length=1024, null=True, upload_to=webframe.models.AbstractPreference.get_filecontent_location, verbose_name='Preference.filecontent'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='helptext',
            field=models.TextField(blank=True, help_text='Preference.helptext.helptext', max_length=8192, null=True, verbose_name='Preference.helptext'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, help_text='ValueObject.id.helptext', primary_key=True, serialize=False, verbose_name='ValueObject.id'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='lang',
            field=models.CharField(blank=True, help_text='Preference.lang.helptext', max_length=20, null=True, verbose_name='Preference.lang'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='lmb',
            field=models.ForeignKey(blank=True, default=webframe.CurrentUserMiddleware.get_current_user, help_text='ValueObject.lmb.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='preference_lmb', to=settings.AUTH_USER_MODEL, verbose_name='ValueObject.lmb'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='lmd',
            field=models.DateTimeField(auto_now=True, help_text='ValueObject.lmd.helptext', verbose_name='ValueObject.lmd'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='name',
            field=models.CharField(help_text='Preference.name.helptext', max_length=100, verbose_name='Preference.name'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='owner',
            field=models.ForeignKey(blank=True, help_text='Preference.owner.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='preference_owner', to=settings.AUTH_USER_MODEL, verbose_name='Preference.owner'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='parent',
            field=models.ForeignKey(blank=True, help_text='Preference.parent.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, to='webframe.preference', verbose_name='Preference.parent'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='regex',
            field=models.CharField(default='^.*$', help_text='Preference.regex.helptext', max_length=1024, verbose_name='Preference.regex'),
        ),
        migrations.AlterField(
            model_name='preference',
            name='sequence',
            field=models.FloatField(default=9223372036854775807, help_text='Preference.sequence.helptext', verbose_name='Preference.sequence'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='cb',
            field=models.ForeignKey(blank=True, default=webframe.CurrentUserMiddleware.get_current_user, help_text='ValueObject.cb.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile_cb', to=settings.AUTH_USER_MODEL, verbose_name='ValueObject.cb'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='cd',
            field=models.DateTimeField(auto_now_add=True, help_text='ValueObject.cd.helptext', verbose_name='ValueObject.cd'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='effDate',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='AliveObject.effDate.helptext', verbose_name='AliveObject.effDate'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='enabled',
            field=models.BooleanField(default=True, help_text='AliveObject.enabled.helptext', verbose_name='AliveObject.enabled'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='expDate',
            field=models.DateTimeField(blank=True, help_text='AliveObject.expDate.helptext', null=True, verbose_name='AliveObject.expDate'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, help_text='ValueObject.id.helptext', primary_key=True, serialize=False, verbose_name='ValueObject.id'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='lmb',
            field=models.ForeignKey(blank=True, default=webframe.CurrentUserMiddleware.get_current_user, help_text='ValueObject.lmb.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile_lmb', to=settings.AUTH_USER_MODEL, verbose_name='ValueObject.lmb'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='lmd',
            field=models.DateTimeField(auto_now=True, help_text='ValueObject.lmd.helptext', verbose_name='ValueObject.lmd'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(help_text='Profile.helptext', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Profile'),
        ),
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='ValueObject.id.helptext', primary_key=True, serialize=False, verbose_name='ValueObject.id')),
                ('lmd', models.DateTimeField(auto_now=True, help_text='ValueObject.lmd.helptext', verbose_name='ValueObject.lmd')),
                ('cd', models.DateTimeField(auto_now_add=True, help_text='ValueObject.cd.helptext', verbose_name='ValueObject.cd')),
                ('key', models.CharField(help_text='Translation.key.helptext', max_length=2048, verbose_name='Translation.key')),
                ('locale', models.CharField(choices=[('en', 'english'), ('zh-hant', 'zh-hant'), ('zh-hans', 'zh-hans')], default='en', help_text='Translation.locale.helptext', max_length=100, verbose_name='Translation.locale')),
                ('msg', models.TextField(blank=True, help_text='Translation.msg.helptext', max_length=4096, null=True, verbose_name='Translation.msg')),
                ('pmsg', models.TextField(blank=True, help_text='Translation.pmsg.helptext', max_length=4096, null=True, verbose_name='Translation.pmsg')),
                ('cb', models.ForeignKey(blank=True, default=webframe.CurrentUserMiddleware.get_current_user, help_text='ValueObject.cb.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translation_cb', to=settings.AUTH_USER_MODEL, verbose_name='ValueObject.cb')),
                ('lmb', models.ForeignKey(blank=True, default=webframe.CurrentUserMiddleware.get_current_user, help_text='ValueObject.lmb.helptext', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translation_lmb', to=settings.AUTH_USER_MODEL, verbose_name='ValueObject.lmb')),
            ],
            options={
                'verbose_name': 'Translation',
                'verbose_name_plural': 'Translations',
                'unique_together': {('key', 'locale')},
            },
            bases=(models.Model, webframe.models.Dictable),
        ),
    ]
