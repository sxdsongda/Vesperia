#!usr/bin/env python
# coding:utf-8

from django.forms import ModelForm, widgets
from . import models
from django import forms
from django.core.exceptions import NON_FIELD_ERRORS


class BaseAssetForm(ModelForm):
    class Meta:
        model = models.Asset
        # fields = ['name', 'idc', 'tags', 'admin']
        fields = ['sn', 'name', 'asset_type', 'manage_ip', 'trade_date', 'expire_date', 'price', 'idc',
                  'contract', 'business_unit', 'admin', 'manufacturer', 'tags']
        localized_fields = ('trade_date', 'expire_date')
        widgets = {
            'sn': widgets.TextInput(attrs={'class': 'form-control'}),
            'name': widgets.TextInput(attrs={'class': 'form-control'}),
            'asset_type': widgets.Select(attrs={'class': 'select-single form-control'}),
            'manage_ip': widgets.TextInput(attrs={'class': 'form-control'}),
            'trade_date': widgets.TextInput(attrs={'class': 'form-control form-datetime'}),
            'expire_date': widgets.TextInput(attrs={'class': 'form-control form-datetime'}),
            'price': widgets.TextInput(attrs={'class': 'form-control'}),
            'idc': widgets.Select(attrs={'class': 'form-control select-single'}),
            'business_unit': widgets.Select(attrs={'class': 'select-single form-control'}),
            'admin': widgets.Select(attrs={'class': 'select-single form-control'}),
            'contract': widgets.Select(attrs={'class': 'select-single form-control'}),
            'tags': widgets.SelectMultiple(attrs={'class': 'select-multiple form-control'}),
            'manufacturer': widgets.Select(attrs={'class': 'form-control select-single'})
        }
        error_messages = {
            'sn': {
                'required': u'SN不能为空',
                'unique': u'该SN已存在'
            },
            'name': {
                'required': u'名称不能为空',
                'unique': u'该名称已存在'
            },
            'trade_date': {
                'invalid': u'日期格式yyyy-mm-dd',
            },
            'expire_date': {
                'invalid': u'日期格式yyyy-mm-dd',
            },
            'manage_ip': {
                'invalid': u'请输入有效的ipv4或ipv6地址',
            },
            'price': {
                'invalid': u'请输入数字'
            }
        }
    
    def clean(self):
        clean_data = super(BaseAssetForm, self).clean()
        if not clean_data:
            clean_data = self.cleaned_data
        trade_date = clean_data.get('trade_date')
        expire_date = clean_data.get('expire_date')
        if trade_date and expire_date and trade_date > expire_date:
            msg = u'购买日期必须小于过保日期'
            self.add_error('trade_date', msg)
            self.add_error('expire_date', msg)


class AssetSoftwareForm(BaseAssetForm):
    class Meta(BaseAssetForm.Meta):
        exclude = ['asset_type', 'manage_ip', 'idc', 'business_unit', 'tags']


class SoftwareForm(ModelForm):
    # 这个表是专属Software,上面的那个是在Asset中Software应该需要填写的部分,继承自BaseAssetForm，选取了其中software需要的部分
    class Meta:
        model = models.Software
        fields = ['version', 'software_type', 'platform', 'language']
        widgets = {
            'software_type': widgets.Select(attrs={'class': 'select-single form-control'}),
            'platform': widgets.Select(attrs={'class': 'select-single form-control'}),
            'version': widgets.TextInput(attrs={'class': 'form-control'}),
            'language': widgets.Select(attrs={'class': 'form-control select-single'}),
        }


class AssetServerUpdateForm(BaseAssetForm):
    class Meta(BaseAssetForm.Meta):
        exclude = ['sn', 'asset_type']


class AssetStorageForm(BaseAssetForm):
    class Meta(BaseAssetForm.Meta):
        exclude = ['asset_type', 'tags']
        help_texts = {
            'manage_ip': u'网络存储请填此项',
            'idc': u'网络存储请选择此项',
            'business_unit': u'网络存储请选择此项',
        }


class AssetNetworkDeviceForm(BaseAssetForm):
    class Meta(BaseAssetForm.Meta):
        exclude = ['asset_type']


class NetworkDeviceForm(ModelForm):
    class Meta:
        model = models.NetworkDevice
        fields = ['device_type', 'vlan_ip', 'intranet_ip', 'port_num', 'model', 'macaddress', 'firmware', 'device_detail']
        widgets = {
            'device_type': widgets.Select(attrs={'class': 'form-control select-single'}),
            'vlan_ip': widgets.TextInput(attrs={'class': 'form-control'}),
            'intranet_ip': widgets.TextInput(attrs={'class': 'form-control'}),
            'port_num': widgets.TextInput(attrs={'class': 'form-control'}),
            'model': widgets.TextInput(attrs={'class': 'form-control'}),
            'macaddress': widgets.TextInput(attrs={'class': 'form-control'}),
            'firmware': widgets.TextInput(attrs={'class': 'form-control'}),
            'device_detail': widgets.Textarea(attrs={'class': 'form-control'}),
        }


class NetworkDeviceNoDetailForm(NetworkDeviceForm):
    class Meta(NetworkDeviceForm.Meta):
        exclude = ['device_detail']


class StorageForm(ModelForm):
    class Meta:
        model = models.Storage
        fields = ['model', 'capacity', 'storage_type', 'interface_type']
        widgets = {
            'model': widgets.TextInput(attrs={'class': 'form-control'}),
            'capacity': widgets.TextInput(attrs={'class': 'form-control'}),
            'storage_type': widgets.Select(attrs={'class': 'form-control'}),
            'interface_type': widgets.Select(attrs={'class': 'form-control'})
        }

    def clean(self):
        clean_data = super(StorageForm, self).clean()
        if not clean_data:
            clean_data = self.cleaned_data
        storage_type = clean_data.get('storage_type')
        interface_type = clean_data.get('interface_type')
        if storage_type == 'ram' and interface_type not in ['ddr3', 'ddr4']:
            self.add_error('interface_type', u'内存只能是DDR3或DDR4')
            self.add_error('storage_type', u'内存只能是DDR3或DDR4')
        elif storage_type in ['disk', 'nas'] and interface_type not in ['sata', 'sas', 'scsi', 'ssd']:
            self.add_error('storage_type', u'硬盘只能是SATA，SAS或SCSI')
            self.add_error('interface_type', u'硬盘只能是SATA，SAS或SCSI')
    # 这里本来遗留了一个问题，硬盘只在form表单这里验证过不了，就不会再到模型层去验证了，而内存在表单验证这里已经有问题了，居然还会继续到模型层去验证，
    # 导致同样的错误提示出现了两个，一个来自表单，一个来自模型层，不知道为什么，但是后面看Django的官方说明，self.add_error会把field从clean_data里面删掉
    # 那么很有可能就是删的问题导致了BUG的出现，本来clean里面的是NonFieldError针对多个field而言，现在指定到某个可能就是会导致问题
    # 现在只要把相关的field都用add_error方法添加相关的错误信息，就可以不出现这种问题，暂时算是解决问题


class BatchServerConfigForm(BaseAssetForm):
    class Meta(BaseAssetForm.Meta):
        exclude = ['sn', 'contract', 'trade_date', 'expire_date', 'price', 'asset_type', 'manufacturer',
                   'manage_ip', 'name']


class VirtualMachineForm(ModelForm):
    host = forms.ModelChoiceField(
        queryset=models.Asset.objects.filter(asset_type='server'),
        label=u'宿主机',
        widget=forms.Select(attrs={'class': 'form-control select-single'}),
        required=False
    )

    class Meta:
        model = models.VirtualMachine
        fields = ['host', 'name', 'vm_type', 'manage_ip', 'macaddress', 'os_type', 'os_distribution',
                  'os_release', 'os_arch']
        widgets = {
            'name': widgets.TextInput(attrs={'class': 'form-control'}),
            'vm_type': widgets.TextInput(attrs={'class': 'form-control'}),
            'manage_ip': widgets.TextInput(attrs={'class': 'form-control'}),
            'macaddress': widgets.TextInput(attrs={'class': 'form-control'}),
            'os_type': widgets.TextInput(attrs={'class': 'form-control'}),
            'os_release': widgets.TextInput(attrs={'class': 'form-control'}),
            'os_arch': widgets.TextInput(attrs={'class': 'form-control'}),
            'os_distribution': widgets.TextInput(attrs={'class': 'form-control'}),
        }
        error_messages = {
            'name': {
                'required': u'名称不能为空',
                'unique': u'该名称已存在'
            },
            'manage_ip': {
                'invalid': u'不是有效的IPv4或IPv6地址',
            },
        }

