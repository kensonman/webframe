from django_tables2 import A
from .models import *
import django_tables2 as tables

class PreferenceTable(tables.Table):
	id=tables.LinkColumn('preference', args=[A('owner.username'), A('id.hex')])

	class Meta(object):
		model=Preference
		fields=('id', 'name', 'sequence', 'value')
		attrs={
			'class': 'table',
		}
		row_attrs={ 'prefId': lambda pref: pref.id.hex }
