# coding:utf-8

import wmi
import win32com
import binascii
import re
from plugins.info_template import BaseInfo


class Win32Info(BaseInfo):
    def __init__(self):
        # 我知道，虽然这里做个BaseInfo的基类并没起到什么作用，但是就为了有补全，并且同一格式
        super(Win32Info, self).__init__()
        self.wmi_obj = wmi.WMI()
        self.wmi_service_obj = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        self.wmi_service_connector = self.wmi_service_obj.ConnectServer(".", "root\cimv2")
        self.wmi_service_connector_wmi = self.wmi_service_obj.ConnectServer(".", "root\wmi")
        self.collect()

    def sys_info(self):
        # 获取操作系统版本
        self.data['os_type'] = 'Windows'
        for sys in self.wmi_obj.Win32_OperatingSystem():
            self.data['os_distribution'] = sys.Caption
            self.data['os_release'] = sys.BuildNumber
            self.data['os_arch'] = sys.OSArchitecture
        for c in self.wmi_obj.Win32_ComputerSystem():
            self.data['model'] = c.Model
            self.data['manufacturer'] = c.Manufacturer
            self.data['ram_size'] = int(c.TotalPhysicalMemory) / (1024*1024)

    def cpu_info(self):
        cpu_list = self.wmi_obj.Win32_Processor()
        self.data['cpu_count'] = len(cpu_list)
        for cpu in cpu_list:
            self.data['cpu_model'] = cpu.Name
            self.data['cpu_core_count'] = cpu.NumberOfCores
            # 正常来说要用主板序列号，但查询出来是None现在先用cpu id代替
            self.data['sn'] = cpu.ProcessorId

    def ram_info(self):
        # 检测内存, 不知道网上为什么要这样写
        # colItems = self.wmi_service_connector.ExecQuery("Select * from Win32_PhysicalMemory")
        memory_list = self.wmi_obj.Win32_PhysicalMemory()
        for memory in memory_list:
            mb = int( 1024 * 1024)
            self.ram_data['sn'] = memory.SerialNumber
            self.ram_data['capacity'] = int(memory.Capacity) / mb
            self.ram_data['manufacturer'] = memory.Manufacturer
            self.ram_data['model'] = memory.Caption
            self.ram_data['slot'] = memory.DeviceLocator.strip()
            self.data['ram'].append(dict(self.ram_data))

    def nic_info(self):
        for nic in self.wmi_obj.Win32_NetworkAdapter():
            if nic.MACAddress is not None:
                self.nic_data['macaddress'] = nic.MACAddress
                self.nic_data['model'] = nic.ServiceName
                self.nic_data['name'] = nic.Name
                self.nic_data['sn'] = nic.GUID
                index = nic.Index
                for w in self.wmi_obj.Win32_NetworkAdapterConfiguration():
                    # 不清楚可以不可以用select * from xx where index = %s来查
                    if w.Index == index:
                        if w.IPAddress is not None:
                            self.nic_data['ipaddress'] = w.IPAddress[0]
                            self.nic_data['netmask'] = w.IPSubnet[0]
                        else:
                            self.nic_data['ipaddress'] = ''
                            self.nic_data['netmask'] = ''
                        break
                self.data['nic'].append(dict(self.nic_data))

    def disk_info(self):
        for disk in self.wmi_obj.Win32_DiskDrive():
            for iface in ('SAS', 'SCSI', 'ATA', 'IDE'):
                if iface in disk.Model:
                    self.disk_data['iface_type'] = iface
                    break
            else:
                self.disk_data['iface_type'] = 'Unknown'
            self.disk_data['slot'] = str(disk.SCSIBus)
            if re.match('Microsoft Windows 7', self.data['os_distribution']):
                reversed_sn = binascii.a2b_hex(disk.SerialNumber).strip()
                sn_char_list = []
                for i in range(len(reversed_sn)):
                    if i % 2 != 0:
                        sn_char_list.append(reversed_sn[i])
                        sn_char_list.append(reversed_sn[i-1])
                sn = "".join(sn_char_list)
            else:
                sn = disk.SerialNumber
            self.disk_data['sn'] = sn
            self.disk_data['model'] = disk.Model
            self.disk_data['manufacturer'] = disk.Manufacturer
            self.disk_data['capacity'] = int(disk.Size) / (1024*1024*1024)
            self.data['disk'].append(dict(self.disk_data))

    def sm_raw_data(self):
        sm_bios_obj = self.wmi_service_connector_wmi.ExecQuery("Select * from MSSMBios_RawSMBiosTables")
        bios_raw_data = sm_bios_obj[0].SMBiosData

    def collect(self):
        self.sys_info()
        self.cpu_info()
        self.disk_info()
        self.ram_info()
        self.nic_info()
        # self.sm_raw_data()


def collect():
    c = Win32Info()
    print (c.data)

if __name__ == '__main__':
    collect()
