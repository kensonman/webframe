# -*- coding: utf-8 -*-
# File:     webframe/serializers.py
# Author:   Kenson Man <kenson@kensonidv.hk>
# Date:     2021-08-15 12:32
# Desc:     Provide the basic model serialization for webframe
from django.contrib.auth.models import User, Group
from django.db.models import Model
from django.db.models.query import QuerySet
from django.core.paginator import Paginator, Page
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from webframe.models import Preference, MenuItem
import logging

logger=logging.getLogger('webframe.serializers')

class PreferenceSerializer(serializers.ModelSerializer):
   class Meta(object):
      model       = Preference
      fields      = ['id', 
         'name', 'value', 'owner', 'parent', 'tipe', 'encrypted', 'helptext',  'regex', 'lang', 'filecontent',
         'sequence', 
         'cb', 'cd', 'lmb', 'lmd',
      ]

class RecursiveField(serializers.Serializer):
   def to_representation(self, value):
      serializer = self.parent.parent.__class__(value, context=self.context)
      return serializer.data

class MenuItemSerializer(serializers.ModelSerializer):
   class Meta(object):
      model       = MenuItem 
      fields      = ['id', 
         'name', 'user', 'username', 'parent', 'icon', 'raw_label', 'label', 'image', 'props', 'onclick', 'mousein', 'mouseout',
         'cb', 'cd', 'lmb', 'lmd', 'childs',
      ]

   username       = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username', source='user')
   raw_label      = serializers.CharField(source='label')
   label          = serializers.CharField(source='translated_label')
   childs         = RecursiveField(many=True)

class UserSerializer(serializers.ModelSerializer):
   class Meta(object):
      model       = User
      fields      = ['id',
         'username', 'first_name', 'last_name', 'email', 
      ]

class APIResult(object):
   '''
   The response object including the metadata and all required information to constructs the response.
   Usage:
   def view(req):
      from django.core.paginator import Paginator
      from rest_framework.response import Response
      from webframe.serializers import APIResult, APIResultSerializer

      data=Model.objects.all() # Get the result
      data=Paginator(data, int(req.GET.get('page_size', 20))).get_page(int(req.GET.get('page', 1)))
      return Response(APIResult(data, target=Model.__class__.__name__, query={}, request=req))
   '''
   def __init__(self, *args, **kwargs):
      if 'result' in kwargs:
         self.result=kwargs['result']
         self.detail=kwargs.get('detail', None)
      elif 'msg' in kwargs: 
         self.msg=kwargs['msg']
         if 'error' in kwargs: self.error=kwargs['error']
         if 'detail' in kwargs: self.detail=kwargs['detail']
      else:
         if len(args)!=1: raise ValueError('No result supplied.')
         req=kwargs['request'].GET if 'request' in kwargs else dict()
         user=kwargs['request'].user if 'request' in kwargs else None
         self.result=args[0]
         self.query=kwargs.get('query', {param: req[param] for param in req if not param.startswith('_')})
         self.meta=dict()
         target=kwargs.get('target', None if len(self.result)<1 else type(self.result[0]))

         # Massage the result
         if isinstance(self.result, Paginator):
            #Convert the Pagainator to page
            if 'request' in ctx:
               self.result=self.result.get_page(int(ctx.get('page', '1')))
            else:
               self.result=self.result.get_page(1)
         elif isinstance(self.result, list) or isinstance(self.result, tuple) or isinstance(self.result, QuerySet):
            pageSize=Preference.objects.pref('page_size', user=user, defval=20)
            logger.warning(req)
            pageSize=req.get(kwargs.get('pageSizeParam', 'page_size'), pageSize)
            logger.warning('PageSize: {0}'.format(pageSize))
            self.result=Paginator(self.result, pageSize)
            self.result=self.result.get_page(int(req.get(kwargs.get('pageParam', 'page'), 1)))

         #Populate the meta
         if isinstance(self.result, Page):
            self.meta['count']=self.result.end_index()
            self.meta['total']=self.result.paginator.count
            self.meta['page']=self.result.number
            self.meta['size']=self.result.paginator.per_page
            self.meta['pages']=[p for p in self.result.paginator.page_range]
            self.meta['hasNext']=self.result.number < len(self.result.paginator.page_range)
            self.meta['hasPrev']=self.result.number>1
            self.meta['nextPage']=self.result.number+1 if self.meta['hasNext'] else self.result.number
            self.meta['prevPage']=self.result.number-1 if self.meta['hasPrev'] else self.result.number
            self.meta['maxPage']=len(self.result.paginator.page_range)+1
         else:
            self.meta['count']=0
            self.meta['total']=0
            self.meta['page']=1
            self.meta['size']=0
            self.meta['pages']=list()
            self.meta['hasNext']=False
            self.meta['hasPrev']=False
            self.meta['nextPage']=1
            self.meta['prevPage']=1
            self.meta['maxPage']=1
         if target is not None: self.meta['target']=target.__name__
         self.result=self.result.object_list
         if 'serializer' in kwargs:
            self.result=[kwargs['serializer'](d, many=False).data for d in self.result]

   @property
   def data(self):
      if hasattr(self, 'result') and hasattr(self, 'detail'):
         rst={'result': self.result}
         if hasattr(self, 'detail'): rst['detail']=self.detail
         return rst
      elif hasattr(self, 'msg'):
         rst={ 'msg': self.msg, }
         if hasattr(self, 'error'): rst['error']=self.error
         if hasattr(self, 'detail'): rst['detail']=self.detail
         return rst
      else:
         return {
            'query': self.query,
            'meta': self.meta,
            'result': self.result
         }
