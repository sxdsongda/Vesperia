#!/usr/bin/env python
# coding:utf-8

from rest_framework import serializers
import models


class UserSerializer(serializers.ModelSerializer):
    # asset_set = serializers.HyperlinkedRelatedField(
    #     view_name='asset:asset-detail', read_only=True, many=True
    # )

    class Meta:
        model = models.UserProfile
        fields = ('name', 'email', 'is_admin', 'asset_set')


class AssetSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name='asset:asset-detail', read_only=True)
    # server = serializers.HyperlinkedRelatedField(view_name='asset:server-detail', read_only=True)
    idc = serializers.PrimaryKeyRelatedField(queryset=models.IDC.objects.all())

    class Meta:
        model = models.Asset
        fields = ('id', 'name', 'sn', 'asset_type', 'manage_ip', 'business_unit', 'manufacturer', 'idc', 'tags')


class VMSerializer(serializers.HyperlinkedModelSerializer):
    host = serializers.HyperlinkedRelatedField(view_name='asset:asset-detail', read_only=True)
    # url = serializers.HyperlinkedIdentityField(view_name='asset:virtualmachine-detail')

    class Meta:
        model = models.VirtualMachine
        fields = ('host', 'manage_ip', 'macaddress', 'os_type', 'os_arch',
                  'os_distribution', 'os_release', 'update_date')


class ServerSerializer(serializers.HyperlinkedModelSerializer):
    asset = serializers.HyperlinkedRelatedField(view_name='asset:asset-detail', read_only=True)
    # url = serializers.HyperlinkedIdentityField(view_name='asset:server-detail',)

    class Meta:
        model = models.Server
        fields = ('id', 'asset', 'manage_ip', 'model', 'raid_type', 'os_type',
                  'os_distribution', 'os_release', 'os_arch', 'update_date')

