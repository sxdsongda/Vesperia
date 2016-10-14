# coding:utf-8


class BaseInfo(object):
    def __init__(self):
        self.data = {
            'asset_type': 'server',
            'os_distribution': None,
            'os_release': None,
            'os_arch': None,
            'os_type': None,
            'model': None,
            'raid_type': None,
            'cpu_model': None,
            'cpu_count': None,
            'cpu_core_count': None,
            'sn': None,
            'ram': [],
            'disk': [],
            'nic': [],
            'raid_adaptor': [],
        }
        self.ram_data = {
            'sn': None,
            'model': None,
            'slot': None,
            'capacity': None,
            'manufacturer': None
        }
        self.disk_data = {
            'sn': None,
            'model': None,
            'slot': None,
            'capacity': None,
            'manufacturer': None,
            'iface_type': None
        }
        self.nic_data = {
            'sn': None,
            'name': None,
            'model': None,
            'macaddress': None,
            'ipaddress': None,
            'netmask': None
        }
        self.raidadaptor_data = {
            'sn': None,
            'slot': None,
            'model': None,
        }





