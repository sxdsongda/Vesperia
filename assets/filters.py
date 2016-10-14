#!/usr/bin/env python
# coding:utf-8

import models
import django_filters
from django_filters import widgets as django_filters_widgets
from django import forms
from MyAuth.models import UserProfile


class AssetFilter(django_filters.FilterSet):
    asset_type = django_filters.MultipleChoiceFilter(
        choices=models.Asset.asset_type_choices,
        widget=forms.CheckboxSelectMultiple,
        label=u'资产类型'
    )
    idc = django_filters.ModelMultipleChoiceFilter(
        queryset=models.IDC.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label=u'IDC机房'
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Manufacturer.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label=u'制造商'
    )
    business_unit = django_filters.ModelMultipleChoiceFilter(
        queryset=models.BusinessUnit.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label=u'业务线'
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label=u'TAG'
    )

    class Meta:
        model = models.Asset
        # fields = ['idc']
        fields = ['asset_type', 'manufacturer', 'business_unit', 'idc', 'tags']


class ServerFilter(django_filters.FilterSet):
    # 注意这里为什么要这样写，lookup_expr这个参数，需要在这里定义好，否则在前端生成的get参数就是例如‘sn__icontains=&&id__icontains=&&’,而不是id=&&sn=&&
    # 所以，之后的处理request.GET就会出现麻烦
    id = django_filters.CharFilter(lookup_expr='exact', label=u'资产ID', widget=forms.TextInput(attrs={'class': 'form-control'}))
    sn = django_filters.CharFilter(lookup_expr='icontains', label=u'SN号', widget=forms.TextInput(attrs={'class': 'form-control'}))
    name = django_filters.CharFilter(lookup_expr='icontains', label=u'名称', widget=forms.TextInput(attrs={'class': 'form-control'}))
    manage_ip = django_filters.CharFilter(lookup_expr='icontains', label=u'管理IP', widget=forms.TextInput(attrs={'class': 'form-control'}))
    idc = django_filters.ModelChoiceFilter(
        queryset=models.IDC.objects.all(),
        label=u'IDC机房',
        widget=forms.Select(attrs={'class': 'form-control select-single'})
    )
    business_unit = django_filters.ModelChoiceFilter(
        queryset=models.BusinessUnit.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select-single'}),
        label=u'业务线'
    )
    admin = django_filters.ModelChoiceFilter(
        queryset=UserProfile.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select-single'}),
        label=u'管理员'
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select-multiple'}),
        label=u'TAG'
    )

    class Meta:
        model = models.Asset
        fields = ['id', 'sn', 'name', 'manage_ip', 'idc', 'business_unit', 'admin', 'tags']


class SoftwareFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(
        lookup_expr='exact',
        label=u'资产ID',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    sn = django_filters.CharFilter(
        lookup_expr='icontains',
        label=u'SN号',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        label=u'名称',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    admin = django_filters.ModelChoiceFilter(
        queryset=UserProfile.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select-single'}),
        label=u'管理员'
    )
    software__type = django_filters.ChoiceFilter(
        choices=models.Software.types_choice,
        label=u'软件类型',
        widget=forms.Select(attrs={'class': 'form-control select-single'})
    )
    software__platform = django_filters.ChoiceFilter(
        choices=models.Software.os_choices,
        label=u'运行平台',
        widget=forms.Select(attrs={'class': 'form-control select-single'})
    )
    software__language = django_filters.ChoiceFilter(
        choices=models.Software.language_choices,
        label=u'语言',
        widget=forms.Select(attrs={'class': 'form-control select-single'})
    )

    class Meta:
        model = models.Asset
        fields = ['id', 'sn', 'name', 'admin', 'software__type', 'software__platform', 'software__language']


class NetworkDeviceFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(
        lookup_expr='exact',
        label=u'资产ID',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    sn = django_filters.CharFilter(
        lookup_expr='icontains',
        label=u'SN号',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        label=u'名称',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    networkdevice__model = django_filters.CharFilter(
        lookup_expr='icontains',
        label=u'型号',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    admin = django_filters.ModelChoiceFilter(
        queryset=UserProfile.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select-single'}),
        label=u'管理员'
    )
    networkdevice__device_type = django_filters.ChoiceFilter(
        choices=models.NetworkDevice.device_type_choices,
        widget=forms.Select(attrs={'class': 'form-control select-single'}),
        label=u'类型'
    )
    manage_ip = django_filters.CharFilter(
        lookup_expr='icontains',
        label=u'管理IP',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    idc = django_filters.ModelChoiceFilter(
        queryset=models.IDC.objects.all(),
        label=u'IDC机房',
        widget=forms.Select(attrs={'class': 'form-control select-single'})
    )
    business_unit = django_filters.ModelChoiceFilter(
        queryset=models.BusinessUnit.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select-single'}),
        label=u'业务线'
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select-multiple'}),
        label=u'TAG'
    )

    class Meta:
        model = models.Asset
        fields = ['id', 'sn', 'name', 'manage_ip', 'networkdevice__model', 'networkdevice__device_type',
                  'admin', 'idc', 'business_unit', 'tags']


class StorageFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(
        lookup_expr='exact',
        label=u'资产ID',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    sn = django_filters.CharFilter(
        lookup_expr='icontains',
        label=u'SN号',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        label=u'名称',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    business_unit = django_filters.ModelChoiceFilter(
        queryset=models.BusinessUnit.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select-single'}),
        label=u'业务线'
    )
    idc = django_filters.ModelChoiceFilter(
        queryset=models.IDC.objects.all(),
        label=u'IDC机房',
        widget=forms.Select(attrs={'class': 'form-control select-single'})
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select-multiple'}),
        label=u'TAG'
    )
    admin = django_filters.ModelChoiceFilter(
        queryset=UserProfile.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select-single'}),
        label=u'管理员'
    )
    storage__model = django_filters.CharFilter(
        lookup_expr='icontains',
        label=u'型号',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    storage__storage_type = django_filters.ChoiceFilter(
        choices=models.Storage.type_choices,
        label=u'设备类型',
        widget=forms.Select(attrs={'class': 'form-control select-single'}),
    )
    storage__interface_type = django_filters.ChoiceFilter(
        choices=models.Storage.interface_choices,
        label=u'接口类型',
        widget=forms.Select(attrs={'class': 'form-control select-single'})
    )

    class Meta:
        model = models.Asset
        fields = ['id', 'sn', 'name', 'storage__storage_type', 'storage__model', 'storage__interface_type',
                  'admin', 'business_unit', 'idc', 'tags']


class VirtualMachineFilter(django_filters.FilterSet):
    host__idc = django_filters.ModelChoiceFilter(
        queryset=models.IDC.objects.all(),
        label=u'宿主机IDC',
        widget=forms.Select(attrs={'class': 'form-control select-single'})
    )
    host__business_unit = django_filters.ModelChoiceFilter(
        queryset=models.BusinessUnit.objects.all(),
        label=u'宿主机业务线',
        widget=forms.Select(attrs={'class': 'form-control select-single'})
    )
    host__tags = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Tag.objects.all(),
        label=u'宿主机TAG',
        widget=forms.SelectMultiple(attrs={'class': 'form-control select-multiple'})
    )
    host__admin = django_filters.ModelChoiceFilter(
        queryset=UserProfile.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select-single'}),
        label=u'宿主机管理员'
    )
    host = django_filters.ModelChoiceFilter(
        queryset=models.Asset.objects.filter(asset_type='server'),
        widget=forms.Select(attrs={'class': 'form-control select-single'}),
        label=u'宿主机'
    )
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        label=u'名称',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    id = django_filters.CharFilter(
        lookup_expr='exact',
        label=u'虚拟机ID',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    manage_ip = django_filters.CharFilter(
        lookup_expr='icontains',
        label=u'管理IP',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = models.VirtualMachine
        fields = ['id', 'name', 'manage_ip', 'host', 'host__idc', 'host__business_unit', 'host__admin', 'host__tags']


class AssetApprovalFilter(django_filters.FilterSet):
    date = django_filters.DateTimeFromToRangeFilter(
        label=u'汇报日期',
        widget=django_filters_widgets.RangeWidget(attrs={'class': 'form-control form-datetime'})
    )
    approved_date = django_filters.DateTimeFromToRangeFilter(
        label=u'批准日期',
        widget=django_filters_widgets.RangeWidget(attrs={'class': 'form-control form-datetime'})
    )
    status_choices = (
        ('', u'--------'),
        ('Success', u'已通过'),
        ('Failed', u'审批失败'),
        ('NotYet', u'未审批')
    )
    status = django_filters.ChoiceFilter(
        choices=status_choices,
        label=u'审批状态',
        widget=forms.Select(attrs={'class': 'select-single form-control'})
    )
    approved_by = django_filters.ModelChoiceFilter(
        queryset=UserProfile.objects.all(),
        label=u'审批人',
        widget=forms.Select(attrs={'class': 'select-single form-control'})
    )

    class Meta:
        model = models.NewAssetApprovalZone
        fields = ['date', 'approved_date', 'status', 'approved_by']