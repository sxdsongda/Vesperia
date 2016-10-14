# coding:utf-8
from __future__ import unicode_literals
from django.db import models
from MyAuth.models import UserProfile
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _


# Create your models here.


class Asset(models.Model):
    asset_type_choices = (
        ('server', u'服务器'),
        ('network_device', u'网络设备'),
        ('storage', u'存储设备'),
        ('software', u'软件资产'),
        ('others', u'其它类'),
    )
    asset_type = models.CharField(choices=asset_type_choices, max_length=64, default='server', verbose_name=u'类型')
    name = models.CharField(max_length=64, unique=True, help_text=u'必填')
    sn = models.CharField(u'资产SN号', max_length=128, unique=True, help_text=u'必填')  # django中,unique为True自动添加索引
    manufacturer = models.ForeignKey('Manufacturer', on_delete=models.SET_NULL, verbose_name=u'制造商', null=True, blank=True)
    # model = models.ForeignKey('ProductModel', verbose_name=u'型号')
    manage_ip = models.GenericIPAddressField(u'管理IP', blank=True, null=True)

    contract = models.ForeignKey('Contract', on_delete=models.SET_NULL, verbose_name=u'合同', null=True, blank=True)
    trade_date = models.DateField(u'购买时间', null=True, blank=True)
    expire_date = models.DateField(u'过保修期', null=True, blank=True)
    price = models.FloatField(u'价格', null=True, blank=True)
    business_unit = models.ForeignKey('BusinessUnit', on_delete=models.SET_NULL, verbose_name=u'所属业务线', null=True, blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    admin = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, verbose_name=u'资产管理员', null=True, blank=True)
    idc = models.ForeignKey('IDC', on_delete=models.SET_NULL, verbose_name=u'IDC机房', null=True, blank=True)

    # status = models.ForeignKey('Status', verbose_name = u'设备状态',default=1)
    # Configuration = models.OneToOneField('Configuration',verbose_name='配置管理',blank=True,null=True)

    memo = models.TextField(u'备注', null=True, blank=True)
    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    update_date = models.DateTimeField(blank=True, auto_now=True)

    class Meta:
        verbose_name = '资产总表'
        verbose_name_plural = "资产总表"

    def __unicode__(self):
        return 'id:%s name:%s' % (self.id, self.name)

    def clean(self):
        if self.trade_date and self.expire_date and self.trade_date > self.expire_date:
            raise ValidationError({'trade_date': _(u'购买日期不能超过过保日期'),
                                   'expire_date': _(u'购买日期不能超过过保日期')})

    # 注意以下的方法给ASSET的每个实例添加了两个字段，如果跟Aggregation的annotate()里面定义的字段一样是会报错的
    # annotate()会使用原生的SQL语句，SUM, MIN, MAX, COUNT, AVG等，优化程度应该是超过这里的，而且更灵活，可以先filter
    # 出asset_type=server，再把这两个字段定义给每个过滤后的ASSET对象
    def _get_ram_size(self):
        if self.ram_set:
            return sum([i.capacity if i.capacity else 0 for i in self.ram_set.select_related()])
        else:
            return 0
    ram_size = property(_get_ram_size)

    def _get_disk_size(self):
        if self.disk_set:
            return sum([i.capacity if i.capacity else 0 for i in self.disk_set.select_related()])
        else:
            return 0
    disk_size = property(_get_disk_size)


class VirtualMachine(models.Model):
    host = models.ForeignKey('Asset', related_name='vm_set', verbose_name=u'宿主机', null=True, blank=True)
    name = models.CharField(u'名称', max_length=64, unique=True)
    vm_type = models.CharField(u'虚拟机类型', max_length=64, blank=True, null=True)

    os_type = models.CharField(u'系统类型', max_length=64, blank=True, null=True)
    os_distribution = models.CharField(u'发型版本', max_length=64, blank=True, null=True)
    os_release = models.CharField(u'系统版本', max_length=64, blank=True, null=True)
    os_arch = models.CharField(u'系统架构', max_length=32, blank=True, null=True)

    memo = models.TextField(u'备注', null=True, blank=True)
    manage_ip = models.GenericIPAddressField(u'管理IP', blank=True, null=True)
    macaddress = models.CharField(u'MAC地址', max_length=64, unique=True, blank=False, null=False)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = '虚拟机'
        verbose_name_plural = '虚拟机'

    def __unicode__(self):
        return 'id:%s ip:%s' % (self.id, self.manage_ip)


class Server(models.Model):
    asset = models.OneToOneField('Asset')
    created_by_choices = (
        ('auto', 'Auto'),
        ('manual', 'Manual'),
    )
    created_by = models.CharField(choices=created_by_choices, max_length=32,
                                  default='auto')  # auto: auto created,   manual:created manually
    # hosted_on = models.ForeignKey('self', related_name='hosted_on_server', blank=True, null=True)  # virtual server
    # sn = models.CharField(u'SN号',max_length=128)
    manage_ip = models.GenericIPAddressField(u'管理IP', max_length=64, blank=True, null=True)
    # manufacturer = models.ForeignKey(verbose_name=u'制造商',max_length=128,null=True, blank=True)
    model = models.CharField(u'型号', max_length=128, null=True, blank=True)
    # 若有多个CPU，型号应该都是一致的，故没做ForeignKey

    # nic = models.ManyToManyField('NIC', verbose_name=u'网卡列表')
    # disk
    raid_type = models.CharField(u'raid类型', max_length=512, blank=True, null=True)
    # physical_disk_driver = models.ManyToManyField('Disk', verbose_name=u'硬盘',blank=True,null=True)
    # raid_adaptor = models.ManyToManyField('RaidAdaptor', verbose_name=u'Raid卡',blank=True,null=True)
    # memory
    # ram_capacity = models.IntegerField(u'内存总大小GB',blank=True)
    # ram = models.ManyToManyField('Memory', verbose_name=u'内存配置',blank=True,null=True)

    os_type = models.CharField(u'操作系统类型', max_length=64, blank=True, null=True)
    os_distribution = models.CharField(u'发型版本', max_length=64, blank=True, null=True)
    os_release = models.CharField(u'操作系统版本', max_length=64, blank=True, null=True)
    os_arch = models.CharField(u'系统架构', max_length=32, blank=True, null=True)

    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = '服务器'
        verbose_name_plural = "服务器"
        # together = ["sn", "asset"]

    def __unicode__(self):
        return '%s sn:%s' % (self.asset.name, self.asset.sn)


class NetworkDevice(models.Model):
    asset = models.OneToOneField('Asset')
    device_type_choices = (
        ('router', u'路由器'),
        ('switch', u'交换机'),
        ('firewall', u'防火墙'),
        ('NLB', u'NetScaler'),
        ('wireless', u'无线AP'),
    )
    device_type = models.CharField(u'设备类型', choices=device_type_choices, max_length=64, default='router')
    vlan_ip = models.GenericIPAddressField(u'VlanIP', blank=True, null=True)
    intranet_ip = models.GenericIPAddressField(u'内网IP', blank=True, null=True)
    macaddress = models.CharField(u'MAC', max_length=64, blank=True, null=True)
    # sn = models.CharField(u'SN号',max_length=128,unique=True)
    # manufacturer = models.CharField(verbose_name=u'制造商',max_length=128,null=True, blank=True)
    model = models.CharField(u'型号', max_length=128, null=True, blank=True)
    firmware = models.CharField(u'固件', blank=True, null=True, max_length=128, )
    port_num = models.SmallIntegerField(u'端口个数', null=True, blank=True)
    device_detail = models.TextField(u'设备详细配置', null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = '网络设备'
        verbose_name_plural = "网络设备"

    def __unicode__(self):
        return '%s id:%s' % (self.asset.name, self.asset.id)


class Software(models.Model):
    # sn = models.CharField(u'SN号',max_length=64, unique=True)
    asset = models.OneToOneField('Asset')
    types_choice = (
        ('system', u'操作系统'),
        ('application', u'应用软件'),
    )
    os_choices = (('Windows', 'Windows'),
                  ('Linux', 'Linux'),
                  ('MacOS', 'MacOS'))
    software_type = models.CharField(u'软件类型', choices=types_choice, max_length=64, blank=True, null=True)
    platform = models.CharField(u'运行平台', choices=os_choices, max_length=32, blank=True, null=True)
    version = models.CharField(u'版本', max_length=64, blank=True, null=True)
    language_choices = (('cn', u'中文'),
                        ('en', u'英文'))
    language = models.CharField(u'语言', choices=language_choices, blank=True, null=True, max_length=32)

    def __unicode__(self):
        return '%s version:%s' % (self.asset.name, self.version)

    class Meta:
        verbose_name = '软件/系统'
        verbose_name_plural = "软件/系统"


class Storage(models.Model):
    asset = models.OneToOneField('Asset')
    model = models.CharField(u'型号', max_length=64)
    capacity = models.IntegerField(u'容量(GB)', blank=True, null=True)
    type_choices = (
        ('ram', u'内存'),
        ('disk', u'硬盘'),
        ('nas', u'网络存储'),
    )
    storage_type = models.CharField(u'类型', choices=type_choices, max_length=64, default='disk')
    interface_choices = (
        ('sata', 'SATA'),
        ('sas', 'SAS'),
        ('scsi', 'SCSI'),
        ('ddr3', 'DDR3'),
        ('ddr4', 'DDR4'),
    )
    interface_type = models.CharField(u'接口类型', choices=interface_choices, max_length=16, default='sata')

    def find_usage(self):
        if self.storage_type == 'disk':
            try:
                on_use = Disk.objects.get(sn=self.asset.sn)
            except ObjectDoesNotExist:
                return None
            return on_use
        elif self.storage_type == 'ram':
            try:
                on_use = RAM.objects.get(sn=self.asset.sn)
            except ObjectDoesNotExist:
                return None
            return on_use

    class Meta:
        verbose_name = u'存储设备'
        verbose_name_plural = u'存储设备'

    def __unicode__(self):
        return self.model

    def clean(self):
        if self.storage_type == 'ram' and self.interface_type not in ['ddr3', 'ddr4']:
            raise ValidationError({'interface_type': _(u'内存只能是DDR3或DDR4')})
        elif self.storage_type in ['disk', 'nas'] and self.interface_type not in ['sata', 'sas', 'scsi']:
            raise ValidationError({'interface_type': _(u'硬盘只能是SATA，SAS或SCSI')})


class CPU(models.Model):
    asset = models.OneToOneField('Asset')
    cpu_model = models.CharField(u'CPU型号', max_length=128)
    cpu_count = models.SmallIntegerField(u'物理cpu个数')
    cpu_core_count = models.SmallIntegerField(u'cpu核数')
    memo = models.TextField(u'备注', null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'CPU部件'
        verbose_name_plural = "CPU部件"

    def __unicode__(self):
        return self.cpu_model


class RAM(models.Model):
    asset = models.ForeignKey('Asset')
    sn = models.CharField(u'SN号', max_length=128)
    model = models.CharField(u'内存型号', max_length=128)
    slot = models.CharField(u'插槽', max_length=64)
    manufacturer = models.CharField(u'制造商', max_length=64, blank=True, null=True)
    capacity = models.IntegerField(u'内存大小(MB)')
    memo = models.CharField(u'备注', max_length=128, blank=True, null=True)
    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return 'RAM:sn:%s capacity:%s slot:%s' % (self.sn, self.capacity, self.slot)

    class Meta:
        verbose_name = 'RAM'
        verbose_name_plural = "RAM"
        unique_together = (("asset", "sn"), ("asset", "slot"))

    auto_create_fields = ['sn', 'slot', 'model', 'capacity']


class Disk(models.Model):
    asset = models.ForeignKey('Asset')
    sn = models.CharField(u'SN号', max_length=128)
    slot = models.CharField(u'插槽位', max_length=64)
    manufacturer = models.CharField(u'制造商', max_length=64, blank=True, null=True)
    model = models.CharField(u'磁盘型号', max_length=128, blank=True, null=True)
    capacity = models.FloatField(u'磁盘容量GB')
    disk_iface_choice = (
        ('ATA', 'SATA'),
        ('SAS', 'SAS'),
        ('SCSI', 'SCSI'),
        ('IDE', 'IDE'),
    )

    iface_type = models.CharField(u'接口类型', max_length=64, choices=disk_iface_choice, default='SAS')
    memo = models.TextField(u'备注', blank=True, null=True)
    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True)

    auto_create_fields = ['sn', 'slot', 'manufacturer', 'model', 'capacity', 'iface_type']

    class Meta:
        verbose_name = '硬盘'
        verbose_name_plural = "硬盘"
        unique_together = (("asset", "sn"), ("asset", "slot"))

    def __unicode__(self):
        return 'Disk:sn:%s capacity:%s slot:%s' % (self.sn, self.capacity, self.slot)


class NIC(models.Model):
    asset = models.ForeignKey('Asset')
    name = models.CharField(u'网卡名', max_length=64, blank=True, null=True)
    sn = models.CharField(u'SN号', max_length=128, blank=True, null=True)
    model = models.CharField(u'网卡型号', max_length=128, blank=True, null=True)
    manufacturer = models.CharField(u'制造商', max_length=64, blank=True, null=True)
    macaddress = models.CharField(u'MAC', max_length=64)
    ipaddress = models.GenericIPAddressField(u'IP', blank=True, null=True)
    netmask = models.CharField(max_length=64, blank=True, null=True)
    bonding = models.CharField(max_length=64, blank=True, null=True)
    memo = models.CharField(u'备注', max_length=128, blank=True, null=True)
    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return 'NIC:mac:%s' % self.macaddress

    class Meta:
        verbose_name = u'网卡'
        verbose_name_plural = u"网卡"
        unique_together = ("asset", "macaddress")

    auto_create_fields = ['name', 'sn', 'model', 'macaddress', 'ipaddress', 'netmask', 'bonding']


class RaidAdaptor(models.Model):
    asset = models.ForeignKey('Asset')
    sn = models.CharField(u'SN号', max_length=128, blank=True, null=True)
    slot = models.CharField(u'插口', max_length=64)
    model = models.CharField(u'型号', max_length=64, blank=True, null=True)
    memo = models.TextField(u'备注', blank=True, null=True)
    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (("asset", "sn"), ("asset", "slot"))


class Manufacturer(models.Model):
    name = models.CharField(u'厂商名称', max_length=64, unique=True)
    support_num = models.CharField(u'支持电话', max_length=30, blank=True)
    memo = models.CharField(u'备注', max_length=128, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = '厂商'
        verbose_name_plural = "厂商"


class BusinessUnit(models.Model):
    parent_unit = models.ForeignKey('self', related_name='parent_level', blank=True, null=True)
    name = models.CharField(u'业务线', max_length=64, unique=True)

    # contact = models.ForeignKey(UserProfile,default=None)
    memo = models.CharField(u'备注', max_length=64, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = '业务线'
        verbose_name_plural = "业务线"


class Contract(models.Model):
    sn = models.CharField(u'合同号', max_length=128, unique=True)
    name = models.CharField(u'合同名称', max_length=64)
    memo = models.TextField(u'备注', blank=True, null=True)
    price = models.IntegerField(u'合同金额')
    detail = models.TextField(u'合同详细', blank=True, null=True)
    start_date = models.DateField(blank=True)
    end_date = models.DateField(blank=True)
    license_num = models.IntegerField(u'license数量', blank=True)
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)

    class Meta:
        verbose_name = '合同'
        verbose_name_plural = "合同"

    def __unicode__(self):
        return self.name


class IDC(models.Model):
    name = models.CharField(u'机房名称', max_length=64, unique=True)
    memo = models.CharField(u'备注', max_length=128)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = '机房'
        verbose_name_plural = "机房"


class Tag(models.Model):
    name = models.CharField('Tag name', max_length=32, unique=True)
    creator = models.ForeignKey(UserProfile)
    create_date = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return self.name


class EventLog(models.Model):
    name = models.CharField(u'事件名称', max_length=100)
    event_type_choices = (
        (1, u'硬件变更'),
        (2, u'新增配件'),
        (3, u'设备下线'),
        (4, u'设备上线'),
        (5, u'定期维护'),
        (6, u'业务上线\更新\变更'),
        (7, u'其它'),
    )
    event_type = models.SmallIntegerField(u'事件类型', choices=event_type_choices)
    asset = models.ForeignKey('Asset', null=True, blank=True)
    component = models.CharField('事件子项', max_length=255, blank=True, null=True)
    detail = models.TextField(u'事件详情')
    date = models.DateTimeField(u'事件时间', auto_now_add=True)
    user = models.ForeignKey(UserProfile, verbose_name=u'事件源')
    memo = models.TextField(u'备注', blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = '事件纪录'
        verbose_name_plural = "事件纪录"

    def colored_event_type(self):
        if self.event_type == 1:
            cell_html = '<span style="background: orange;">%s</span>'
        elif self.event_type == 2:
            cell_html = '<span style="background: yellowgreen;">%s</span>'
        else:
            cell_html = '<span >%s</span>'
        return cell_html % self.get_event_type_display()

    colored_event_type.allow_tags = True
    colored_event_type.short_description = u'事件类型'


class NewAssetApprovalZone(models.Model):
    sn = models.CharField(u'资产SN号', max_length=128, blank=True, null=True)
    # 这里为了支持虚拟机,需要把这个设置成允许为空,如果要Unique就只能有一个为空, 为了保证这个对服务器来说是唯一的,可以用clean方法实现
    asset_type_choices = (
        ('server', u'服务器'),
        ('network_device', u'网络设备'),
        ('storage', u'存储设备'),
        ('virtual_machine', u'虚拟机'),
    )
    asset_type = models.CharField(choices=asset_type_choices, max_length=64, blank=True, null=True)
    manufacturer = models.CharField(max_length=64, blank=True, null=True)
    model = models.CharField(max_length=128, blank=True, null=True)
    ram_size = models.IntegerField(blank=True, null=True)
    cpu_model = models.CharField(max_length=128, blank=True, null=True)
    cpu_count = models.IntegerField(blank=True, null=True)
    cpu_core_count = models.IntegerField(blank=True, null=True)
    os_distribution = models.CharField(max_length=64, blank=True, null=True)
    os_type = models.CharField(max_length=64, blank=True, null=True)
    os_release = models.CharField(max_length=64, blank=True, null=True)
    data = models.TextField(u'资产数据')
    date = models.DateTimeField(u'汇报日期', auto_now_add=True)
    status_choices = (
        ('Success', u'已通过'),
        ('Failed', u'审批失败'),
        ('SuccessWithProblems', u'存在问题'),
        ('NotYet', u'未审批')
    )
    status = models.CharField(u'审批状态', choices=status_choices, max_length=64, default='NotYet')
    approved_by = models.ForeignKey(UserProfile, verbose_name=u'批准人', blank=True, null=True)
    approved_date = models.DateTimeField(u'批准日期', blank=True, null=True)

    def __unicode__(self):
        return 'sn:%s asset_type:%s' % (self.sn, self.asset_type)
        # sn允许为空,如果客户端未提供sn,或者提供的sn=None,直接return self.sn有可能会出现NoneType error,要么像这样弄,要么sn=''

    class Meta:
        verbose_name = '新上线待批准资产'
        verbose_name_plural = "新上线待批准资产"
