# -*- coding: utf-8 -*-
# File:     webframe/serializers.py
# Author:   Kenson Man <kenson@kensonidv.hk>
# Date:     2021-08-15 12:32
# Desc:     Provide the basic model serialization for webframe
from django.db.models import Model
from django.core.paginator import Paginator, Page
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination

class ValueObjectSerializer(serializers.Serializer):
   id             =serializers.UUIDField()
   lmd            =serializers.DateTimeField()
   lmb            =serializers.CharField(source='lmb.username', allow_null=True)
   cd             =serializers.DateTimeField()
   cb             =serializers.CharField(source='cb.username', allow_null=True)

class AliveObjectSerializer(serializers.Serializer):
   effDate        =serializers.DateTimeField()
   expDate        =serializers.DateTimeField(allow_null=True)
   enabled        =serializers.BooleanField()

class AliveValueObjectSerializer(ValueObjectSerializer):
   effDate        =serializers.DateTimeField()
   expDate        =serializers.DateTimeField(allow_null=True)
   enabled        =serializers.BooleanField()

class OrderableValueObjectSerializer(ValueObjectSerializer):
   sequence       =serializers.FloatField()

class OrderableAliveValueObjectSerializer(ValueObjectSerializer):
   effDate        =serializers.DateTimeField()
   expDate        =serializers.DateTimeField(allow_null=True)
   enabled        =serializers.BooleanField()
   sequence       =serializers.FloatField()

class PreferenceSerializer(OrderableValueObjectSerializer):
   name           =serializers.CharField()
   value          =serializers.CharField(allow_null=True)
   owner          =serializers.CharField(source='owner.username', allow_null=True)
   parent         =serializers.UUIDField(allow_null=True)
   tipe           =serializers.IntegerField()
   encrypted      =serializers.BooleanField()
   helptext       =serializers.CharField(allow_null=True)
   regex          =serializers.CharField()
   lang           =serializers.CharField(allow_null=True)
   filecontent    =serializers.FileField(allow_null=True)

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
      if len(args)!=1: raise ValueError('No result supplied.')
      self.result=args[0]
      self.query=kwargs.get('query', None)
      self.meta=dict()
      req=kwargs['request'].GET if 'request' in kwargs else dict()
      user=kwargs['request'].user if 'request' in kwargs else None
      target=kwargs.get('target', None if len(self.result)<1 else type(self.result[0]))

      # Massage the result
      if isinstance(self.result, Paginator):
         #Convert the Pagainator to page
         if 'request' in ctx:
            self.result=self.result.get_page(int(ctx.get('page', '1')))
         else:
            self.result=self.result.get_page(1)
      elif isinstance(self.result, list) or isinstance(self.result, tuple):
         pageSize=Preference.objects.pref('page_size', user=user, defval=20)
         pageSize=req.get(kwargs.get('pageSizeParam', 'page_size'), pageSize)
         self.result=Paginator(self.result, pageSize)
         self.result=self.result.get_page(int(req.get(kwargs.get('pageParam', 'page'), 1)))

      #Populate the meta
      if isinstance(self.result, Page):
         self.meta['count']=self.result.end_index()
         self.meta['total']=self.result.paginator.count
         self.meta['page']=self.result.number
         self.meta['size']=self.result.paginator.per_page
         self.meta['pages']=[p for p in self.result.paginator.page_range]
      else:
         self.meta['count']=0
         self.meta['total']=0
         self.meta['page']=1
         self.meta['size']=0
         self.meta['pages']=list()
      self.meta['target']=target.__name__
      self.result=self.result.object_list
      if 'serializer' in kwargs:
         self.result=[kwargs['serializer'](d, many=False).data for d in self.result]

   @property
   def data(self):
      return {
         'query': self.query,
         'meta': self.meta,
         'result': self.result
      }
