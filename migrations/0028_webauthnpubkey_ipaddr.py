# Generated by Django 3.2.6 on 2022-08-23 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webframe', '0027_webauthnpubkey_lastsignin'),
    ]

    operations = [
        migrations.AddField(
            model_name='webauthnpubkey',
            name='ipaddr',
            field=models.GenericIPAddressField(blank=True, help_text='WebAuthnPubkey.ipaddr.helptext', null=True, verbose_name='WebAuthnPubkey.ipaddr'),
        ),
        migrations.AlterField(
            model_name='webauthnpubkey',
            name='lastSignin',
            field=models.DateTimeField(blank=True, help_text='WebAuthnPubkey.lastSignin.helptext', null=True, verbose_name='WebAuthnPubkey.lastSignin'),
        ),
    ]
