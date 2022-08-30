# -*- coding: utf-8 -*-
# src/webframe/lookups.py
from ajax_select import register, LookupChannel
from .models import * 
import logging 

logger=logging.getLogger('webframe.lookups')

class BaseLookup(LookupChannel):
   def get_query(self, q, req):
      if isUUID(q):
         return self.model.objects.filter(id=q)
      else:
         return self.model.objects.filter(name__startswith=q)

   def format_item_display(self, item):
      return item.__str__()

@register('preferences')
class PreferenceLookup(BaseLookup):
   model=Preference

@register('numberings')
class NumberingLookup(BaseLookup):
   model=Numbering
