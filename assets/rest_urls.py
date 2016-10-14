#!/usr/bin/env python
# coding:utf-8

from django.conf.urls import url, include
import rest_views as views
from rest_framework.routers import DefaultRouter

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'assets', views.AssetViewSet)
router.register(r'servers', views.ServerViewSet)
router.register(r'vm', views.VMViewSet)
# router.register(r'network_device', views.NetworkDeviceViewSet)
# router.register(r'software', views.SoftwareViewSet)
# router.register(r'cpu', views.CPUViewSet)
# router.register(r'ram', views.RAMViewSet)
# router.register(r'disk', views.DiskViewSet)
# router.register(r'nic', views.NICViewSet)
# router.register(r'raid_adaptor', views.RaidAdaptorViewSet)
# router.register(r'manufacturer', views.ManufacturerViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]

# urlpatterns = [
#     url(r'^$', views.api_root),
#     url(r'^assets/$', views.AssetList.as_view(), name='asset-list'),
#     url(r'^assets/(?P<pk>[0-9]+)/$', views.AssetDetail.as_view(), name='asset-detail'),
#     url(r'^server/$', views.ServerList.as_view(), name='server-list'),
#     url(r'^server/(?P<pk>[0-9]+)/$', views.ServerDetail.as_view(), name='server-detail'),
#     url(r'^users/$', views.UserList.as_view(), name='user-list'),
#     url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view(), name='user-detail'),
#     url(r'^api-auth/', include('rest_framework.urls',
#                                namespace='rest_framework')),
# ]