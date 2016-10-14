#!/usr/bin/env python
# coding:utf-8
from __future__ import unicode_literals
from . import models, filters, forms
from django.db.models import Sum, Avg, Max, Min, Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def fetch_asset_with_components(asset_id, asset_type):
    pass


class AssetHandlerForDataTable(object):
    def __init__(self, request, asset_type):
        self.query_dic = request.GET
        self.asset_type = asset_type
        self.return_dic = {'draw': int(request.GET['draw'])}
        self._fuzzy_list = ['sn', 'name', 'admin__name', 'admin__email', 'price', 'trade_date', 'expire_date',
                            'contract__name', 'manufacturer__name', 'idc__name', 'business_unit__name',
                            'manage_ip', 'tags__name']

    def _fuzzy_search(self, fuzzy, total_asset_queryset):
        # 清晰的写法
        q_filter = Q()
        for value in self._fuzzy_list:
            q_filter |= Q(**{"{}__icontains".format(value): fuzzy})
        # 使用reduce和lambda
        # q_filter = reduce(lambda x, y: x | Q(**{"{}__icontains".format(y): fuzzy}), self._fuzzy_list, Q())
        # 使用operator.or_
        # q_filter = reduce(operator.or_, [Q(**{"{}__icontains".format(key): fuzzy}) for key in self._fuzzy_list])
        filtered_list = total_asset_queryset.filter(q_filter).distinct().select_related()
        """
       注意这里为什么要加一个distinct(),因为多对多关系的建立是靠一个中间表来实现的，那么当执行SQL查询的时候，
       实际上也是先查这个中间表select * from assets_asset left outer join assets_asset_tags on (assets_asset.id =
       assets_asset_tag.asset_id) left outer join assets_tag on (assets_asset_tags.tag_id = assets_tag.id) where
       (assets_asset.name like %xx% OR  assets_tag.name LIKE %xx%) 很明显，中间表里面会有重复的结果，因为他匹配的不是主键
       那么再去查对应的tag表，就会出问题了，这就不像外键关联和一对一关联，根据ON主键匹配过滤后，只有一个结果能匹配，
       所以后面就相当于拿多个重复的数据去匹配asset_tag.name 就会出现，如果匹配到了name，会出现匹配到的只有一个结果，
       没匹配到的，由于OR，会出现重复结果，加个distinct(),相当于 SELECT DISTINCT assets_asset.id ... FROM ... JOIN... ON... WHERE...
       print (unicode(filtered_list.query))
       """
        return filtered_list

    def _accurate_search(self, filter_name, total_asset_queryset):
        f = filter_name(self.query_dic, queryset=total_asset_queryset)
        return f.qs

    def _paging(self, ordered_queryset):
        page_size = int(self.query_dic['pageSize'])
        page = int(self.query_dic['startIndex']) + 1  # dataTable是从0开始，而Paginator是从1开始
        paginator = Paginator(ordered_queryset, page_size)
        try:
            paged_queryset = paginator.page(page)
        except PageNotAnInteger:
            paged_queryset = paginator.page(1)
        except EmptyPage:
            paged_queryset = paginator.page(paginator.num_pages)
        return paged_queryset

    def _ordering(self, filtered_queryset):
        order_item = self.query_dic.get('orderColumn')
        order_dir = self.query_dic.get('orderDir')
        order_item = '-' + order_item if order_dir == 'desc' else order_item if order_item else 'id'
        return filtered_queryset.order_by(order_item)

    def _packaging_data_list(self, paged_queryset):
        return getattr(self, 'packaging_%s_data' % self.asset_type)(paged_queryset)

    def handle(self):
        if hasattr(self, '_get_%s_list_and_filter' % self.asset_type):
            total_asset_list, filter_name = getattr(self, '_get_%s_list_and_filter' % self.asset_type)()
            self.return_dic['recordsTotal'] = len(total_asset_list)
            if self.query_dic.get('fuzzySearch') == 'true':
                fuzzy = self.query_dic.get('fuzzy')
                filtered_queryset = self._fuzzy_search(fuzzy, total_asset_list)
            else:
                filtered_queryset = self._accurate_search(filter_name, total_asset_list)
            self.return_dic['recordsFiltered'] = len(filtered_queryset)
            ordered_queryset = self._ordering(filtered_queryset)
            paged_queryset = self._paging(ordered_queryset)
            self.return_dic['data'] = self._packaging_data_list(paged_queryset)
            return self.return_dic
        else:
            raise ValueError('Try: server, network_device, software, virtual_machine or storage')

    def _get_software_list_and_filter(self):
        self._fuzzy_list.extend(['software__language', 'software__software_type', 'software__platform', 'software__version'])
        filter_name = filters.SoftwareFilter
        total_software_list = models.Asset.objects.filter(asset_type='software')
        return total_software_list, filter_name

    def _get_network_device_list_and_filter(self):
        self._fuzzy_list.extend(['networkdevice__vlan_ip', 'networkdevice__intranet_ip', 'networkdevice__model',
                                 'networkdevice__macaddress', 'networkdevice__firmware'])
        filter_name = filters.NetworkDeviceFilter
        total_network_device_list = models.Asset.objects.filter(asset_type='network_device')
        return total_network_device_list, filter_name

    def _get_server_list_and_filter(self):
        self._fuzzy_list.extend(['server__model', 'cpu__cpu_model', 'nic__ipaddress'])
        filter_name = filters.ServerFilter
        total_server_list = models.Asset.objects.filter(asset_type='server')
        return total_server_list, filter_name

    def _get_storage_list_and_filter(self):
        self._fuzzy_list.extend(['storage__model', 'storage__capacity', 'storage__storage_type', 'storage__interface_type'])
        filter_name = filters.StorageFilter
        total_storage_list = models.Asset.objects.filter(asset_type='storage')
        return total_storage_list, filter_name

    def _get_virtual_machine_list_and_filter(self):
        self._fuzzy_list = [
            'vm_type', 'os_type', 'os_distribution', 'manage_ip', 'macaddress', 'host__idc__name',
            'host__business_unit__name', 'host__tags__name', 'host__admin__email',
            'host__admin__name', 'host__name'
        ]
        filter_name = filters.VirtualMachineFilter
        total_vm_list = models.VirtualMachine.objects.select_related().prefetch_related('host__tags')
        return total_vm_list, filter_name

    def _get_asset_approval_list_and_filter(self):
        self._fuzzy_list = [
            'date', 'approved_by__email', 'approved_by__name', 'approved_date', 'asset_type', 'manufacturer',
            'model'
        ]
        total_asset_list = models.NewAssetApprovalZone.objects.all()
        filter_name = filters.AssetApprovalFilter
        return total_asset_list, filter_name

    @classmethod
    def packaging_server_data(cls, paged_queryset):
        data_list = []
        """
        这里要考虑到dataTable返回过来的排序的参数，他返回来的排序的列名，即我们这里定义的这些key名，所以，这里凡是以涉及到外键，
        多对多，一对一关联的，都用Django的双下划线'__'来表示出具体要的那个关联字段field，比如说，业务线，肯定是按照业务线的名称来排序，
        而不是按业务线的id来排序，那么，dataTable那端的对应column要选择business_unit__name，之前没有考虑到这点，直接把business_unit的value
        就写成了obj.business_unit.name，很显然，排序是不会按照想象的来的。
        除此之外，还有一点是更重要的，key名的定义，严格来说，应该是凡是可以从Django ORM中找到对应的字段的，key名和field字段名都应该是一样的，
        例如idc这个字段，其实对应数据库表里面是idc_id，但是你不需要写成idc_id, Django ORM只需要idc，对于value来说，就应该是obj.idc.id，
        注意到这点很重要！因为，无论是Django Form生成对应的表的field，还是django-filter的form.field，Restful都是按照Django ORM的
        方式来的，也很人性化。用Django form，filter的时候已经发现了，任何输入元素input，select，他们的name属性就是field名，如果是选择的输入元素，
        value就是对应的choice(同一个表中)或者对应的id(外键，多对多)，所以我们这里的key：value的定义，得考虑到这点，之后我们才可以用这个数据
        去给Django form赋值了。
        还要特别说明一下，Django Form是不能用__来处理关联字段的，只能用多个Form来实现，对于外键和多对多没影响，因为他们就是一个同一个Django Model的
        一个字段，但是对于一对一，得要单独考虑哪些字段是用于排序的，哪些字段是用来给form赋值的，这里体现出了要同时处理两个或者更多个表的情况，
        他们的关系是一对一，例如，处理software，那么key名的定义就很关键，如果software_type用来给DataTable排序，那么应该key是software__software_type，
        如果同时要用software_type来初始化一个修改或新增信息的表单，那么应该还有个key名是software_type，因为要用两个form，一个是software独自的，
        software_type是他的一个字段，另一个是asset表中包含software的那部分，所以，在设计表结构的时候就要注意到，一对一关系，两个Model中的字段名一定
        不能相同。如果仅用于显示（不用于赋值表单，排序），那么就可以较随意的定义key名了。
        对于Choice这种用一个元组表示的('cn',u'中文')，没有办法直接用来模糊查询和表单赋值，只能用来显示，get_FOO_display(),如果需要排序，赋值，
        得多两个key才行，同样还是不能模糊查询，因为Django数据库中存的是'cn'不是'中文'
        """
        for obj in paged_queryset:
            data = {
                'id': obj.id,
                'sn': obj.sn,
                'name': obj.name,
                'business_unit': None if not obj.business_unit else obj.business_unit.id,
                'business_unit__name': None if not obj.business_unit else obj.business_unit.name,
                'idc': None if not obj.idc else obj.idc.id,
                'idc__name': None if not obj.idc else obj.idc.name,
                'server__model': None if not obj.server else obj.server.model,
                'cpu__cpu_model': None if not obj.cpu else obj.cpu.cpu_model,
                'cpu__cpu_core_count': None if not obj.cpu else obj.cpu.cpu_core_count,
                'cpu__cpu_count': None if not obj.cpu else obj.cpu.cpu_count,
                'manage_ip': obj.manage_ip,
                'manufacturer': None if not obj.manufacturer else obj.manufacturer.id,
                'manufacturer__name': None if not obj.manufacturer else obj.manufacturer.name,
                # 'ram_size': obj.ram_size, annotate 多个sum会出现BUG
                'ram_size': sum([i.capacity if i.capacity else 0 for i in obj.ram_set.select_related()]),
                # 'disk_size': obj.disk_size,
                'disk_size': sum([i.capacity if i.capacity else 0 for i in obj.disk_set.select_related()]),
                'tags': [i.id for i in obj.tags.all()],
                'tags__name': '|'.join(i.name for i in obj.tags.all()),
                'admin': None if not obj.admin else obj.admin.id,
                'admin__email': None if not obj.admin else obj.admin.email,
                'nic_ip': None if not obj.nic_set else '|'.join(i.ipaddress for i in obj.nic_set.select_related()),
                'price': obj.price,
                'trade_date': obj.trade_date,
                'expire_date': obj.expire_date,
                'contract': None if not obj.contract else obj.contract.id,
                'contract__name': None if not obj.contract else obj.contract.name
            }
            data_list.append(data)
        return data_list

    @classmethod
    def packaging_software_data(cls, paged_queryset):
        data_list = []
        for obj in paged_queryset:
            data = {
                'id': obj.id,
                'sn': obj.sn,
                'name': obj.name,
                'admin': None if not obj.admin else obj.admin.id,
                'admin__email': None if not obj.admin else obj.admin.email,
                'price': obj.price,
                'trade_date': obj.trade_date,
                'expire_date': obj.expire_date,
                'manufacturer': None if not obj.manufacturer else obj.manufacturer.id,
                'manufacturer__name': None if not obj.manufacturer else obj.manufacturer.name,
                'contract': None if not obj.contract else obj.contract.id,
                'contract__name': None if not obj.contract else obj.contract.name,
                'software__software_type': None if not obj.software else obj.software.get_software_type_display(),  # 用于排序
                'software_type': None if not obj.software else obj.software.software_type,  # 用于表单赋值
                'software__platform': None if not obj.software else obj.software.get_platform_display(),
                'platform': None if not obj.software else obj.software.platform,
                'version': None if not obj.software else obj.software.version,
                'language': None if not obj.software else obj.software.language,
                'software__language': None if not obj.software else obj.software.get_language_display()
            }
            data_list.append(data)
        return data_list

    @classmethod
    def packaging_network_device_data(cls, paged_queryset):
        data_list = []
        for obj in paged_queryset:
            data = {
                'id': obj.id,
                'sn': obj.sn,
                'name': obj.name,
                'admin': None if not obj.admin else obj.admin.id,
                'admin__email': None if not obj.admin else obj.admin.email,
                'price': obj.price,
                'trade_date': obj.trade_date,
                'expire_date': obj.expire_date,
                'business_unit': None if not obj.business_unit else obj.business_unit.id,
                'business_unit__name': None if not obj.business_unit else obj.business_unit.name,
                'idc': None if not obj.idc else obj.idc.id,
                'idc__name': None if not obj.idc else obj.idc.name,
                'tags': [i.id for i in obj.tags.all()],
                'tags__name': '|'.join(i.name for i in obj.tags.all()),
                'manufacturer': None if not obj.manufacturer else obj.manufacturer.id,
                'manufacturer__name': None if not obj.manufacturer else obj.manufacturer.name,
                'contract': None if not obj.contract else obj.contract.id,
                'contract__name': None if not obj.contract else obj.contract.name,
                'manage_ip': obj.manage_ip,
                'device_type': None if not obj.networkdevice else obj.networkdevice.device_type,
                'networkdevice__device_type': None if not obj.networkdevice else obj.networkdevice.get_device_type_display(),
                'vlan_ip': None if not obj.networkdevice else obj.networkdevice.vlan_ip,
                'intranet_ip': None if not obj.networkdevice else obj.networkdevice.intranet_ip,
                'macaddress': None if not obj.networkdevice else obj.networkdevice.macaddress,
                'firmware': None if not obj.networkdevice else obj.networkdevice.firmware,
                'port_num': None if not obj.networkdevice else obj.networkdevice.port_num,
                'networkdevice__port_num': None if not obj.networkdevice else obj.networkdevice.port_num,
                'model': None if not obj.networkdevice else obj.networkdevice.model,
            }
            data_list.append(data)
        return data_list

    @classmethod
    def packaging_storage_data(cls, paged_queryset):
        data_list = []
        for obj in paged_queryset:
            data = {
                'id': obj.id,
                'sn': obj.sn,
                'name': obj.name,
                'admin': None if not obj.admin else obj.admin.id,
                'admin__email': None if not obj.admin else obj.admin.email,
                'manage_ip': obj.manage_ip,
                'price': obj.price,
                'trade_date': obj.trade_date,
                'expire_date': obj.expire_date,
                'business_unit': None if not obj.business_unit else obj.business_unit.id,
                'business_unit__name': None if not obj.business_unit else obj.business_unit.name,
                'idc': None if not obj.idc else obj.idc.id,
                'idc__name': None if not obj.idc else obj.idc.name,
                'tags': [i.id for i in obj.tags.all()],
                'tags__name': '|'.join(i.name for i in obj.tags.all()),
                'manufacturer': None if not obj.manufacturer else obj.manufacturer.id,
                'manufacturer__name': None if not obj.manufacturer else obj.manufacturer.name,
                'contract': None if not obj.contract else obj.contract.id,
                'contract__name': None if not obj.contract else obj.contract.name,
                'model': None if not obj.storage else obj.storage.model,
                'storage_type': None if not obj.storage else obj.storage.storage_type,
                'storage__storage_type': None if not obj.storage else obj.storage.get_storage_type_display(),
                'capacity': None if not obj.storage else obj.storage.capacity,
                'storage__capacity': None if not obj.storage else obj.storage.capacity,
                'interface_type': None if not obj.storage else obj.storage.interface_type,
                'storage__interface_type': None if not obj.storage else obj.storage.get_interface_type_display(),
            }
            data_list.append(data)
        return data_list

    @classmethod
    def packaging_virtual_machine_data(cls, paged_queryset):
        data_list = []
        for obj in paged_queryset:
            data = {
                'id': obj.id,
                'name': obj.name,
                'vm_type': obj.vm_type,
                'os_type': obj.os_type,
                'os_distribution': obj.os_distribution,
                'os_release': obj.os_release,
                'os_arch': obj.os_arch,
                'manage_ip': obj.manage_ip,
                'macaddress': obj.macaddress,
                'host__idc__name': None if not obj.host else obj.host.idc.name,
                'host__business_unit__name': None if not obj.host else obj.host.business_unit.name,
                'host__tags__name': None if not obj.host else '|'.join(i.name for i in obj.host.tags.all()),
                'host__admin__email': None if not obj.host else obj.host.admin.email,
                'host__name': None if not obj.host else obj.host.name,
                'host__manage_ip': None if not obj.host else obj.host.manage_ip,
                'host': None if not obj.host else obj.host.id
            }
            data_list.append(data)
        return data_list

    @classmethod
    def packaging_asset_approval_data(cls, paged_queryset):
        data_list = []
        for obj in paged_queryset:
            data = {
                'id': obj.id,
                'sn': obj.sn,
                'asset_type': obj.get_asset_type_display(),
                'manufacturer': obj.manufacturer,
                'model': obj.model,
                'ram_size': obj.ram_size,
                'cpu_model': obj.cpu_model,
                'cpu_count': obj.cpu_count,
                'cpu_core_count': obj.cpu_core_count,
                'os_distribution': obj.os_distribution,
                'os_type': obj.os_type,
                'os_release': obj.os_release,
                'date': obj.date,
                'status': obj.get_status_display(),
                'approved_by': None if not obj.approved_by else obj.approved_by.email,
                'approved_date': obj.approved_date,
                'data': obj.data
            }
            data_list.append(data)
        return data_list
