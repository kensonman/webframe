from django.contrib import admin
from .models import *

@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
   list_display=('id', 'name', 'parent', 'lmb', 'lmd')
