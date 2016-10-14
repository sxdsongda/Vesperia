#!/usr/bin/env python
# coding:utf-8
import json
from . import models, forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction, IntegrityError
from django.utils import timezone
from django import forms as django_forms


class Asset(object):
    response = {'error': [], 'info': [], 'warning': []}

    def __init__(self, request):
        self.request = request
        self.clean_data = None
        self.asset_obj = None

    @classmethod
    def response_msg(cls, msg_type, key, msg):
        if msg_type in cls.response:
            cls.response[msg_type].append({key: msg})
        else:
            raise ValueError

    def handle(self):
        if self.data_is_valid():
            asset_type = self.clean_data['asset_type']
            func = getattr(self, asset_type)
            func()
        return self.response

    def get_asset_obj_by_sn(self):
        """
        通过sn号到DB中找到对应的asset_obj,网络设备和服务器可以用,虚拟机不能用
        :return: asset_obj
        """
        try:
            self.asset_obj = models.Asset.objects.get(sn=self.clean_data['sn'])
            return True
        except ObjectDoesNotExist:
            return False

    def data_is_valid(self):
        data = self.request.POST.get('asset_data')
        if data:
            try:
                data = json.loads(data)
                self.mandatory_check(data)
            except TypeError as e:
                self.response_msg('error', 'AssetDataInvalid', str(e))  # 这里json.loads会有可能出现异常
        else:
            self.response_msg('error', 'AssetDataInvalid', "Could not get asset data, probably data not provided")
        if self.response['error']:
            return False
        else:
            self.clean_data = data  # valid验证通过,定义这个字段
            return True

    @classmethod
    def mandatory_check(cls, raw_data):
        cls.data_source_format_check(raw_data)
        if not cls.response['error']:
            cls.data_source_validate(raw_data)
        if not cls.response['error'] and raw_data.get('asset_type') == 'server':
            cls.data_source_duplication_check(raw_data)

    @classmethod
    def data_source_format_check(cls, raw_data):
        """检测必须的字段是否未提供或者为空,并且是否数据类型符合"""
        field_sets = {
            'server': [('sn', 'unicode'), ('cpu_model', 'unicode'), ('cpu_count', 'int'), ('disk', 'list'),
                       ('cpu_core_count', 'int'), ('os_arch', 'unicode'), ('nic', 'list'), ('ram', 'list'),
                       ('os_type', 'unicode'), ('os_distribution', 'unicode'), ('os_release', 'unicode'),
                       ('raid_adaptor', 'list')],
            'network_device': [('sn', 'unicode'), ('macaddress', 'unicode'), ('intranet_ip', 'unicode')],
            'virtual_machine': [('nic', 'list'), ('os_type', 'unicode'), ('os_distribution', 'unicode'),
                                ('os_release', 'unicode'), ('os_arch', 'unicode')]
        }
        list_item_check_field = {
            'nic': [('macaddress', 'unicode')],
            'ram': [('slot', 'unicode'), ('capacity', 'int'), ('model', 'unicode'), ('sn', 'unicode')],
            'disk': [('slot', 'unicode'), ('capacity', 'int'), ('sn', 'unicode')],
            'raid_adaptor': [('slot', 'unicode'), ('sn', 'unicode')]
        }
        asset_type = raw_data.get('asset_type')
        if not asset_type:
            cls.response_msg('error', 'MandatoryCheckFailed', 'Asset type not provided')
        elif asset_type in field_sets:
            check_list = field_sets[asset_type]
            for item, data_type in check_list:
                if not raw_data.get(item) and item not in ['raid_adaptor']:  # 检查必要字段是否存在，其中raid_adaptor是可有可无的则用not in
                    cls.response_msg('error', 'MandatoryCheckFailed', '%s not provided' % item)
                elif type(raw_data[item]).__name__ != data_type:
                    cls.response_msg('error', 'MandatoryCheckFailed', '%s type error, should be %s' % (item, data_type))
                elif type(raw_data[item]).__name__ == data_type == 'list':
                    for sub_item, sub_data_type in list_item_check_field[item]:
                        for i in raw_data[item]:
                            if type(i) is not dict:
                                cls.response_msg('error', 'MandatoryCheckFailed', 'item in %s should be dict' % item)
                                continue
                            if not i.get(sub_item):
                                cls.response_msg('error', 'MandatoryCheckFailed', "%s sub item %s not provided" % (item, sub_item))
                            elif type(i[sub_item]).__name__ != sub_data_type:
                                cls.response_msg('error', 'MandatoryCheckFailed', '%s sub item %s should be %s' % (item, sub_item, sub_data_type))
                            else:
                                pass
        else:
            cls.response_msg('error', 'MandatoryCheckFailed', 'Unknown asset type')

    @classmethod
    def data_source_validate(cls, raw_data):
        """检测特殊字段如IP，EMAIL等的是否合法"""
        key_to_check = {'server': ['nic'], 'virtual_machine': ['nic'], 'network_device': ['vlan_ip', 'intranet_ip']}
        asset_type = raw_data.get('asset_type')
        temp_dic = {}
        for i in key_to_check[asset_type]:
            if type(raw_data.get(i)) is list:
                for dic in raw_data.get(i):
                    form = SpecialFieldValidateForm(dic)
                    if form.is_valid():
                        pass
                    else:
                        error_dic = form.errors
                        for k, v in error_dic.items():
                            cls.response_msg('error', i, v)
                        break
            else:
                temp_dic[i] = raw_data.get(i)
        if temp_dic:
            form = SpecialFieldValidateForm(temp_dic)
            if form.is_valid():
                pass
            else:
                error_dic = form.errors
                for k, v in error_dic.item():
                    cls.response_msg('error', k, v)

    @classmethod
    def data_source_duplication_check(cls, raw_data):
        keys_to_check = {
            'nic': ['macaddress'], 'ram': ['sn', 'slot'], 'disk': ['sn', 'slot'], 'raid_adaptor': ['sn', 'slot']
        }
        for key in keys_to_check:
            fields_to_check = keys_to_check[key]
            item_list = raw_data.get(key)
            for field in fields_to_check:
                temp_list = []
                for item in item_list:
                    temp_list.append(item.get(field))
                if len(temp_list) != len(set(temp_list)):
                    cls.response_msg('error', 'Duplicated', '%s field %s has duplicated value' % (key, field))

    def server(self):
        if not self.get_asset_obj_by_sn():
            self.send_server_to_new_asset_approval_zone()  # new asset
        else:
            self._update_server()  # update asset

    @classmethod
    @transaction.atomic
    def _create_server(cls, asset_obj, raw_data):
        cls.__create_server_info(asset_obj, raw_data)
        cls.__create_cpu_component(asset_obj, raw_data)
        cls.__create_disk_component(asset_obj, raw_data)
        cls.__create_nic_component(asset_obj, raw_data)
        cls.__create_ram_component(asset_obj, raw_data)
        cls.__create_or_update_manufacturer(asset_obj, raw_data)

    def _update_server(self):
        self.__update_server_info()
        self.__update_cpu_component()
        self.__create_or_update_manufacturer(self.asset_obj, self.clean_data)
        # ram, disk, nic, raid_adaptor is not one-to-one relation to model Asset, and may need update, create or delete
        self.__update_asset_component(
            data_source=self.clean_data['ram'],
            fk='ram_set',
            update_fields=['sn', 'model', 'capacity'],
            identify_field='sn'
        )
        self.__update_asset_component(
            data_source=self.clean_data['disk'],
            fk='disk_set',
            update_fields=['model', 'slot', 'capacity', 'manufacturer', 'iface_type'],
            identify_field='sn'
        )
        self.__update_asset_component(
            data_source=self.clean_data['nic'],
            fk='nic_set',
            update_fields=['ipaddress', 'netmask', 'bonding', 'name', 'sn', 'model'],
            identify_field='macaddress'
        )

    def virtual_machine(self):
        nic_info = self.clean_data['nic']
        address_list = []
        obj_list = []
        for i in nic_info:
            address_list.append(i.get('macaddress'))
        for mac in address_list:
            try:
                vm_obj = models.VirtualMachine.objects.get(macaddress=mac)
                obj_list.append(vm_obj)
                break
            except ObjectDoesNotExist:
                pass
        if len(obj_list) > 0:
            # obj already exists, check if need to update
            vm_obj = obj_list[0]
            update_fields = ['os_type', 'os_distribution', 'os_release', 'os_arch', 'manage_ip']
            for i in update_fields:
                val_from_db = getattr(vm_obj, i)
                val_from_data_source = self.clean_data.get(i)
                if i == 'manage_ip':
                    val_from_data_source = self.clean_data['nic'][0]['ipaddress']
                if val_from_data_source == val_from_db:
                    pass
                else:
                    setattr(vm_obj, i, val_from_data_source)
                    vm_obj.update_date = timezone.localtime(timezone.now())
                    vm_obj.save()
                    self.response_msg('info', 'VirtualMachineUpdated', 'Field %s update to %s' % (i, val_from_data_source))
        else:
            # new virtual machine
            self.send_server_to_new_asset_approval_zone()

    def network_device(self):
        if not self.get_asset_obj_by_sn():
            self.send_server_to_new_asset_approval_zone()  # new asset
        else:
            pass  # 对于网络设备来说,通常是一个整体,如果存在就不会变更里面的配置

    @classmethod
    def _create_network_device(cls, asset_obj, raw_data):
        pass

    @classmethod
    def create_asset_from_approval_zone(cls, approval_zone_id, request):
        try:
            approval_zone_obj = models.NewAssetApprovalZone.objects.get(id=approval_zone_id)
            if approval_zone_obj.status in ['Success', 'Failed', 'SuccessWithProblems']:
                pass
            else:
                raw_data = json.loads(approval_zone_obj.data)
                cls.mandatory_check(raw_data)
                if cls.response['error']:
                    return cls.response
                asset_type = approval_zone_obj.asset_type
                if asset_type not in ['server', 'virtual_machine', 'network_device']:
                    approval_zone_obj.status = 'Failed'
                    approval_zone_obj.save()
                    cls.response_msg('error', 'UnknownAssetType', 'UnknownAssetType')
                    return cls.response
                if asset_type != 'virtual_machine':
                    # virtual machine 放在另外一个表中,所以要单独对待
                    try:
                        # 这里存在一种可能性：管理员操作失误，自己到后台建立了相应的资产，然后这里再save()就会出错
                        asset_obj = models.Asset(
                            asset_type=asset_type,
                            sn=approval_zone_obj.sn,
                            name=approval_zone_obj.sn
                        )
                        asset_obj.save()
                        func = getattr(cls, '_create_%s' % asset_type)
                        func(asset_obj=asset_obj, raw_data=raw_data)
                    except IntegrityError:
                        approval_zone_obj.status = 'Failed'
                        approval_zone_obj.save()
                        cls.response_msg('error', 'AssetCreateFailed', 'AssetNameOrSerialNumberAlreadyExist')
                else:
                    cls._create_virtual_machine(approval_zone_obj)  # 因为vm用的是VirtualMachine表不是Asset表,所以要单独create
                    if cls.response['error']:
                        approval_zone_obj.status = 'Failed'
                    else:
                        approval_zone_obj.status = 'Success'
                        approval_zone_obj.approved_date = timezone.localtime(timezone.now())
                        approval_zone_obj.approved_by = request.user
                    approval_zone_obj.save()
                    return cls.response
                if cls.response['error']:
                    approval_zone_obj.status = 'SuccessWithProblems'
                else:
                    approval_zone_obj.status = 'Success'
                approval_zone_obj.approved_date = timezone.localtime(timezone.now())
                approval_zone_obj.approved_by = request.user
                approval_zone_obj.save()
        except ObjectDoesNotExist:
            cls.response_msg('error', 'ObjectMissing', 'ApprovalZoneObjectDoesNotExist')
        return cls.response

    @classmethod
    def _create_virtual_machine(cls, raw_data):
        try:
            vm_obj = models.VirtualMachine(
                os_type=raw_data.get('os_type'),
                os_distribution=raw_data.get('os_distribution'),
                os_release=raw_data.get('os_release'),
                os_arch=raw_data.get('os_arch'),
                macaddress=raw_data['nic'][0]['macaddress'],
                manage_ip=raw_data['nic'][0]['ipaddress']
            )
            vm_obj.save()
        except Exception as e:
            cls.response_msg('error', 'ValidationError', 'VirtualMachineValidationFailed %s' % str(e))

    @classmethod
    def __create_nic_component(cls, asset_obj, raw_data):
        nic_info = raw_data.get('nic')
        for nic_item in nic_info:
            data_set = {
                'asset': asset_obj,
                'name': nic_item.get('name'),
                'macaddress': nic_item.get('macaddress'),
                'ipaddress': nic_item.get('ipaddress'),
                'sn': nic_item.get('sn'),
                'model': nic_item.get('model'),
                'netmask': nic_item.get('netmask'),
                'bonding': nic_item.get('boding')
            }
            try:
                obj = models.NIC(**data_set)
                obj.save()
            except Exception as e:
                cls.response_msg('error', 'ValidationError', 'NicValidationFailed %s' % str(e))

    @classmethod
    def __create_disk_component(cls, asset_obj, raw_data):
        disk_info = raw_data.get('disk')
        for disk_item in disk_info:
            try:
                data_set = {
                    'asset_id': asset_obj.id,
                    'slot': disk_item.get('slot'),
                    'capacity': disk_item.get('capacity'),
                    'iface_type': disk_item.get('iface_type'),
                    'sn': disk_item.get('sn'),
                    'model': disk_item.get('model'),
                    'manufacturer': disk_item.get('manufacturer'),
                }
                obj = models.Disk(**data_set)
                obj.save()
            except Exception as e:
                cls.response_msg('error', 'ValidationError', 'DiskValidationFailed %s' % str(e))

    @classmethod
    def __create_cpu_component(cls, asset_obj, raw_data):
        try:
            data_set = {
                'asset_id': asset_obj.id,
                'cpu_model': raw_data.get('cpu_model'),
                'cpu_count': raw_data.get('cpu_count'),
                'cpu_core_count': raw_data.get('cpu_core_count')
            }
            obj = models.CPU(**data_set)
            obj.save()
        except Exception as e:
            cls.response_msg('error', 'ValidationError', 'CPUValidationFailed %s' % str(e))

    def __update_cpu_component(self):
        update_fields = ['cpu_model', 'cpu_count', 'cpu_core_count']
        if hasattr(self.asset_obj, 'cpu'):  # one to one field, model name is the related name
            self.__compare_component(self.asset_obj.cpu, update_fields, self.clean_data)
        else:
            self.__create_cpu_component(self.asset_obj, self.clean_data)

    @classmethod
    def __create_ram_component(cls, asset_obj, raw_data):
        ram_info = raw_data.get('ram')
        for ram_item in ram_info:
            try:
                data_set = {
                    'asset_id': asset_obj.id,
                    'slot': ram_item.get('slot'),
                    'capacity': ram_item.get('capacity'),
                    'sn': ram_item.get('sn'),
                    'model': ram_item.get('model'),
                }
                obj = models.RAM(**data_set)
                obj.save()
            except Exception as e:
                cls.response_msg('error', 'ValidationError', 'RAMValidationFailed %s' % str(e))

    @classmethod
    def __create_server_info(cls, asset_obj, raw_data):
        try:
            data_set = {
                'asset_id': asset_obj.id,
                'model': raw_data.get('model'),
                'raid_type': raw_data.get('raid_type'),
                'os_type': raw_data.get('os_type'),
                'os_distribution': raw_data.get('os_distribution'),
                'os_release': raw_data.get('os_release'),
                'os_arch': raw_data.get('os_arch')
            }
            obj = models.Server(**data_set)
            obj.save()
        except Exception as e:
            cls.response_msg('error', 'ValidationError', 'SeverValidationFailed %s' % str(e))

    def __update_server_info(self):
        update_fields = ['model', 'raid_type', 'os_type', 'os_distribution', 'os_release', 'os_arch']
        if hasattr(self.asset_obj, 'server'):
            self.__compare_component(self.asset_obj.server, update_fields, self.clean_data)
        else:
            self.__create_server_info(self.asset_obj, self.clean_data)

    @classmethod
    def __create_or_update_manufacturer(cls, asset_obj, raw_data):
        manufacturer = raw_data.get('manufacturer')
        if manufacturer:
            try:
                obj = models.Manufacturer.objects.get(name__iregex=manufacturer)
                asset_obj.manufacturer = obj
                asset_obj.save()
            except ObjectDoesNotExist:
                pass

    def __update_asset_component(self, data_source, fk, update_fields, identify_field=None):
        """
            内存,硬盘,网卡,raid卡(不熟悉,暂不考虑)的更新比较特殊,他们跟资产是多对一,可能存在一个或多个配件(例如多条内存)同时更新,
        而且是包含三种基本更新类型,增,删,改,这与上面的cpu,server更新不一样,那些只有改(增的可能性我去除了,因为过不了Mandatory Check),这里存在些需要注意的地方:
            首先,本质上来说,无论是单个更新还是多个更新,必须要数据库里的全部配件对象都要做更新检查,但是数据库里面是不可能一次性全部更新的,
        因为每个内存都是一个独立的数据库对象,一次可以操作一个对象的多个字段field同时更新,却不可能一次操作多个对象同时更新.
            其次,必须要找一个能够唯一确定这个配件的标识字段,网卡好办,用mac地址就可以确定,硬盘和内存都有sn号,他们是可以唯一确定这个配件的,
        但有点不幸的是,目前我的电脑,用wmi取不出正确的内存的sn号(试试用slot),经测试，有些电脑可以有些电脑不行，可能与SMBus有关
            然后,最关键的一点,由于是只能一个一个接着的比,那么通过唯一标识,用一个数据库的对象和所有客户端提供的数据来做比较,能决定这个数据库对象是要删还是改,却不能决定
        未匹配到的客户端数据是否需要增;同理,反过来用一个客户端的数据和所有数据库的对象做比较,可以决定这个数据是否要增加或修改一个数据库对象,却不能决定未匹配到的数据库对象
        是否需要删.
            所以,综合前面所说,需要通过两种方式的比较才能确定所有的增,删,改,这两种方式,如果全部都比一次,重复了比较,虽然不会造成数据重复,但是实际上是可以避免的.
        无论是哪种比较方式,都得要这种方式全部比较完,才能确定是否为增,删,所以还要设置一个标识位
            当然,其实也是通过增加一个component_add(del)_list,把两种比较方法缩减至一种比较方法的,就是如果匹配不到,就添加进去,如果匹配到了,就判断是否存在list中,
        如果存在,就remove掉,再到最后根据这个list做添加或删除操作,但这并不是想的那么简单,虽然,列表可以判断一个字典在不在里面,但逻辑要更复杂些,容易出错,比方说,如果都没匹配到,那么,
        列表里面的数据会重复[a,b,a,b],要去重,方法是,在每次放到列表里面之前都判断下,这个在不在列表里;再比方说,前面的匹配到了,要防止后面的把前面匹配到的再添加到list中,
        方法是再用一个列表,标识那些匹配到了的,这个列表不会重复,还需要在放到add_list前判断,这个是否已经匹配到了
        """
        component_match_flag = False
        compared_obj_list = []  # 这里面放入的应该是唯一可以标识这个obj的字段,由于identify_field还存在不确定性,故放入id
        compared_data_source_list = []  # 这里面放入的也应该是唯一可以标识这个数据源的key的value
        # component_add_list = []
        # compared_data_source_item_list = []
        try:
            component_obj = getattr(self.asset_obj, fk)
            objects_from_db = component_obj.select_related()
            for obj in objects_from_db:  # 先用一个数据库对象与所有客户端数据来比较, 可以判断出哪个对象需要更新,哪个对象需要删除,已经更新的应该放在列表里面
                key_field_data = getattr(obj, identify_field)
                for data_source_item in data_source:
                    key_field_data_from_source = data_source_item.get(identify_field)
                    if key_field_data == key_field_data_from_source:
                        self.__compare_component(obj, update_fields, data_source_item)
                        component_match_flag = True
                        compared_obj_list.append(obj.id)
                        compared_data_source_list.append(key_field_data_from_source)
                        # compared_data_source_item_list.append(data_source_item)
                        # if data_source_item in component_add_list:
                        #     component_add_list.remove(data_source_item)
                        break
                    # else:
                        # if data_source_item not in component_add_list:
                        #     if data_source_item not in compared_data_source_item_list:
                        #         component_add_list.append(data_source_item)
                if not component_match_flag:
                    self.__update_del_asset_component(obj, fk)  # 说明这个数据库对象通过唯一标识没匹配到客户端数据,需要删除
                else:
                    component_match_flag = False  # 改这个flag,以进行下一个数据库对象的比较
            # for i in component_add_list:
            #     self.__update_add_asset_component(i, fk)
            for data_source_item in data_source:  # 再用一个客户端数据与所有的数据库对象比较,之前已经把更已经更新的添加到了列表,先判断
                if data_source_item.get(identify_field) not in compared_data_source_list:
                    key_field_data_from_source = data_source_item.get(identify_field)
                    for obj in objects_from_db:
                        if obj.id not in compared_obj_list:
                            key_field_data = getattr(obj, identify_field)
                            if key_field_data == key_field_data_from_source:
                                self.__compare_component(obj, update_fields, data_source_item)
                                component_match_flag = True
                                break  # 这个时候就不需要再把匹配到的数据放到列表里了
                    if not component_match_flag:
                        self.__update_add_asset_component(data_source_item, fk)  # 说明这个客户端数据通过唯一标识没有匹配到数据库对象,需要增加
                    else:
                        component_match_flag = False  # 说明匹配到了,改这个flag,以进行下一个客户端数据的比较
        except ValueError as e:
            print ('\033[41;1m%s\033[0m' % str(e))

    def __update_add_asset_component(self, data_source_item, fk):
        models_dic = {'ram_set': 'RAM', 'disk_set': 'Disk', 'nic_set': 'NIC'}
        model_name = models_dic.get(fk)
        try:
            model = getattr(models, model_name)
            data_source_item['asset_id'] = self.asset_obj.id
            obj = model(**data_source_item)
            obj.save()
            log_msg = 'Asset [%s] has added new component [%s]' % (self.asset_obj, obj)
            self.response_msg('info', 'NewAssetComponentAdded', log_msg)
            self.log_record('NewComponentAdded', log_msg, component='%s: %s' % (model_name, obj))
        except Exception as e:
            self.response_msg('error', 'AddingComponentException', 'Asset [%s] component [%s] adding error %s' % (self.asset_obj, model_name, str(e)))
            print ("\033[31;1m %s \033[0m" % e)

    def __update_del_asset_component(self, model_obj, fk):
        models_dic = {'ram_set': 'RAM', 'disk_set': 'Disk', 'nic_set': 'NIC'}
        model_name = models_dic.get(fk)
        log_msg = "Asset [%s] component [%s] is not found in client's reporting data, assume it has been removed or replaced, delete it from DB" % (self.asset_obj, model_obj)
        self.response_msg('info', 'AssetComponentDelete', log_msg)
        self.log_record('HardwareChanges', log_msg, component='%s: %s' % (model_name, model_obj))
        model_obj.delete()

    def __compare_component(self, model_obj, fields_to_compare, data_source):
        update_field_list = []
        for field in fields_to_compare:
            val_from_db = getattr(model_obj, field)
            val_from_data_source = data_source.get(field)
            if val_from_db == val_from_data_source:
                pass
            else:
                setattr(model_obj, field, val_from_data_source)
                update_field_list.append((field, val_from_db, val_from_data_source))
        if len(update_field_list) > 0:
            model_obj.update_date = timezone.now()
            model_obj.save()
            for item in update_field_list:
                field, val_from_db, val_from_data_source = item
                log_msg = "Asset [%s] component [%s] field [%s] has changed from [%s] to [%s]" % (
                    self.asset_obj, model_obj, field, val_from_db, val_from_data_source)
                self.response_msg('info', 'AssetComponentUpdated', log_msg)
                self.log_record('HardwareChanges', log_msg, component='%s' % model_obj)

    def send_server_to_new_asset_approval_zone(self):
        asset_sn = self.clean_data.get('sn')
        new_asset = models.NewAssetApprovalZone.objects.get_or_create(
            sn=asset_sn,
            data=json.dumps(self.clean_data),
            manufacturer=self.clean_data.get('manufacturer'),
            model=self.clean_data.get('model'),
            asset_type=self.clean_data.get('asset_type'),
            ram_size=self.clean_data.get('ram_size'),
            cpu_model=self.clean_data.get('cpu_model'),
            cpu_count=self.clean_data.get('cpu_count'),
            cpu_core_count=self.clean_data.get('cpu_core_count'),
            os_distribution=self.clean_data.get('os_distribution'),
            os_release=self.clean_data.get('os_release'),
            os_type=self.clean_data.get('os_type'),
        )
        self.response_msg('info', 'AssetSendToApprovalZone', 'It needs IT admins to approval')

    def log_record(self, event_name, detail, component=None):
        """
        (1, u'硬件变更'),
        (2, u'新增配件'),
        (3, u'设备下线'),
        (4, u'设备上线'),
        """
        event_type_dic = {
            1: ['FieldChanged', 'HardwareChanges'],
            2: ['NewComponentAdded'],
            3: ['AssetOffline'],
            4: ['AssetOnline']
        }
        user = self.request.user
        if not user.id:
            # 客户端发过来的数据,虽然有手动添加了一个user,但那个并不是完整的user obj, 所以要判断下,如果是客户端发来的数据,就要用一个管理员账号
            user = models.UserProfile.objects.filter(is_admin=True).first()
        event_type = None
        for k, v in event_type_dic.items():
            if event_name in v:
                event_type = k
                break
        if self.clean_data['asset_type'] == 'virtual_machine':
            asset_id = None
        else:
            asset_id = self.asset_obj.id
        log_obj = models.EventLog(
            name=event_name,
            event_type=event_type,
            asset_id=asset_id,
            component=component,
            detail=detail,
            user_id=user.id
        )
        log_obj.save()


class SpecialFieldValidateForm(django_forms.Form):
    ipaddress = django_forms.GenericIPAddressField(
        required=False, error_messages={'invalid': u'Invalid IPv4 or IPv6 address'})
    intranet_ip = django_forms.GenericIPAddressField(
        required=False, error_messages={'invalid': u'Invalid IPv4 or IPv6 address'})
    vlan_ip = django_forms.GenericIPAddressField(
        required=False, error_messages={'invalid': u'Invalid IPv4 or IPv6 address'})

