from django_tables2 import A
from django.contrib.auth.models import User
from .models import *
import django_tables2 as tables

class PreferenceTable(tables.Table):
	name=tables.LinkColumn('preference', args=[A('owner.username'), A('id.hex')])

	class Meta(object):
		model=Preference
		fields=('name', 'sequence', 'value')
		attrs={	'class': 'table', }
		row_attrs={ 'prefId': lambda pref: pref.id.hex }

class UserTable(tables.Table):
	username=tables.LinkColumn('user', args=[A('username'),])

	class Meta(object):
		model=User
		fields=('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined')
		attrs={	'class': 'table', }
		row_attrs={ 'username': lambda user: user.username, 'userId': lambda user: user.id}
