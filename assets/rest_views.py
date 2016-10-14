#!/usr/bin/env python
# coding:utf-8


import serializers
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
import models
from rest_framework import generics
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.reverse import reverse


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides 'list' and 'detail' actions.
    """
    queryset = models.UserProfile.objects.all()
    serializer_class = serializers.UserSerializer


class AssetViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provide 'list', 'create', 'retrieve',
    'update' and 'destroy' actions
    """
    queryset = models.Asset.objects.all()
    serializer_class = serializers.AssetSerializer


class VMViewSet(viewsets.ModelViewSet):
    queryset = models.VirtualMachine.objects.all()
    serializer_class = serializers.VMSerializer


class ServerViewSet(viewsets.ModelViewSet):
    queryset = models.Server.objects.all()
    serializer_class = serializers.ServerSerializer


class UserList(generics.ListAPIView):
    queryset = models.UserProfile.objects.all()
    serializer_class = serializers.UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = models.UserProfile.objects.all()
    serializer_class = serializers.UserSerializer


class AssetList(generics.ListCreateAPIView):
    """
    List all assets, or create a new asset
    """
    queryset = models.Asset.objects.all()
    serializer_class = serializers.AssetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class AssetDetail(generics.RetrieveUpdateAPIView):
    """
    get detail of an asset, or update it
    """
    queryset = models.Asset.objects.all()
    serializer_class = serializers.AssetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class ServerList(generics.ListCreateAPIView):
    queryset = models.Server.objects.all()
    serializer_class = serializers.ServerSerializer


class ServerDetail(generics.RetrieveUpdateAPIView):
    queryset = models.Server.objects.all()
    serializer_class = serializers.ServerSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def api_root(request, format=None):
    return Response({
        'users': reverse('asset:user-list', request=request, format=format),
        'assets': reverse('asset:asset-list', request=request, format=format),
        'server': reverse('asset:server-list', request=request, format=format)
    })


# @api_view(['GET', 'POST'])
# def asset_list(request, format=None):
#     """
#     List all assets, or create a new asset.
#     """
#     if request.method == 'GET':
#         assets = models.Asset.objects.all()
#         serializer = serializers.AssetSerializer(assets, many=True)
#         return Response(serializer.data)
#
#     elif request.method == 'POST':
#         serializer = serializers.AssetSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(['GET', 'PUT'])
# def asset_detail(request, pk, format=None):
#     """
#     Retrieve, update a asset instance.
#     """
#     try:
#         asset = models.Asset.objects.get(pk=pk)
#     except models.Asset.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == 'GET':
#         serializer = serializers.AssetSerializer(asset)
#         return Response(serializer.data)
#
#     elif request.method == 'PUT':
#         serializer = serializers.AssetSerializer(asset, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 关于登陆用户的接口是不是该单独在那个做好的认证模块MyAuth那做出来还是这里做一个关联,值得思考
# 目前的想法是,在这里做一个关联,首先无论怎么说,一个具体的app如果跟登陆的用户有关,一定要有一个关联,
# 其次,这个关联应该是要做在这个具体的app里面的,不可能在用户认证那里关联回来,且不说这个认证模块是独立的APP,
# 表单结构里面就不能把(拿QQ来说)类似QQ空间,QQ微博等的字段信息存进去,就只说在他那里关联回来也不应该,就好像我用QQ号登陆了别的网站,
# 别的网站只能获得我的基本信息,不可能还能因为到他那登陆了,我的QQ空间,QQ好友等信息的API接口全部都可以在别的网站被查到,
# 所以,他那里如果做了接口,接口又关联回来了这些APP,对内来说是方便了,对外来说则开放了很多没有必要的接口信息,接口不安全, 虽然可以加权限,然而实在是在给自己挖坑,也不符合REST规范
# 如果做了接口,又不把这些信息让人查询到,就只能是完全做为一个独立的模块,在他那里不应该包含app相关的内容,所以,
# 我认为,认证那里做接口,对内没什么用,主要通常是为了对外开放,让别人知道我有这么一个我的认证的用户可以oauth,也就是可以只读ReadOnly,一定是不能写改的
