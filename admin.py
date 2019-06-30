from django.contrib import admin
from .models import *

@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
   list_display=('id', 'name', 'parent', 'reserved', 'lmb', 'lmd')
   list_filter=('reserved',)
   search_fields=('name', 'value')
