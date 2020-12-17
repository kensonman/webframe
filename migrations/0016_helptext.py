# Generated by Django 3.1.3 on 2020-12-17 15:56

from django.db import migrations, models

def update_regex(apps, schema_editor):
   Preference=apps.get_model('webframe', 'Preference')
   Preference.objects.filter(_tipe=7).update(regex='') #for each email preference

class Migration(migrations.Migration):

    dependencies = [
        ('webframe', '0015_numbering_defaultpattern'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='preference',
            name='reserved',
        ),
        migrations.RenameField(
            model_name='preference',
            old_name='tipe',
            new_name='_tipe',
        ),
        migrations.AddField(
            model_name='preference',
            name='helptext',
            field=models.TextField(blank=True, help_text='webframe.models.Preference.helptext.helptext', max_length=8192, null=True, verbose_name='webframe.models.Preference.helptext'),
        ),
        migrations.AddField(
            model_name='preference',
            name='regex',
            field=models.CharField(default='^.*$', help_text='webframe.models.Preference.regex.helptext', max_length=1024, verbose_name='webframe.models.Preference.regex'),
        ),
        migrations.RunPython(update_regex),
    ]
