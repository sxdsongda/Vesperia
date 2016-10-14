#!/usr/bin/env python
# coding:utf-8

from plugins.info_template import BaseInfo
import subprocess
import commands
import os
import re


def collect():
    l = LinuxInfo()
    for key, val in l.data.items():
        if not val:
            l.data.pop(key)
    return l.data


class LinuxInfo(BaseInfo):
    def __init__(self):
        super(LinuxInfo, self).__init__()
        self.collect()

    def sys_info(self):
        # 获取操作系统版本
        distributor = subprocess.check_output(" lsb_release -a|grep 'Distributor ID'", shell=True).split(":")
        # distributor = commands.getoutput(" lsb_release -a|grep 'Distributor ID'").split(":")
        release = subprocess.check_output(" lsb_release -a|grep Description", shell=True).split(":")
        # release  = commands.getoutput(" lsb_release -a|grep Description").split(":")
        self.data['os_distribution'] = distributor[1].strip() if len(distributor) > 1 else None
        self.data['os_type'] = 'Linux'
        self.data['os_release'] = release[1].strip() if len(release) > 1 else None
        # data_dic = {
        #     "os_distribution": distributor[1].strip() if len(distributor)>1 else None,
        #     "os_release": release[1].strip() if len(release)>1 else None,
        #     "os_type": "linux",
        # }
        self.data['os_arch'] = subprocess.check_output("getconf LONG_BIT", shell=True).strip() + '-bit'

    def cpu_info(self):
        base_cmd = 'cat /proc/cpuinfo'

        raw_data = {
            'cpu_model': "%s |grep 'model name' |head -1 " % base_cmd,
            'cpu_count': "%s |grep  'processor'|wc -l " % base_cmd,
            'cpu_core_count': "%s |grep 'cpu cores' |awk -F: '{SUM +=$2} END {print SUM}'" % base_cmd,
        }

        for k, cmd in raw_data.items():
            try:
                cmd_res = subprocess.check_output(cmd, shell=True)
                # cmd_res = commands.getoutput(cmd)
                raw_data[k] = cmd_res.strip()

            # except Exception,e:
            except ValueError as e:
                print (e)

        self.data['cpu_count'] = raw_data['cpu_count']
        self.data['cpu_core_count'] = raw_data['cpu_core_count']
        cpu_model = raw_data["cpu_model"].split(":")
        if len(cpu_model) > 1:
            self.data['cpu_model'] = cpu_model[1].strip()
        else:
            self.data['cpu_model'] = -1

    def ram_info(self):
        # raw_data = subprocess.check_output(["sudo", "dmidecode" ,"-t", "17"])
        raw_data = commands.getoutput("sudo dmidecode -t 17")
        raw_list = raw_data.split("\n")
        raw_ram_list = []
        item_list = []
        for line in raw_list:

            if line.startswith("Memory Device"):
                raw_ram_list.append(item_list)
                item_list =[]
            else:
                item_list.append(line.strip())

        # ram_list = []
        for item in raw_ram_list:
            item_ram_size = 0
            # ram_item_to_dic = {}
            for i in item:
                # print i
                data = i.split(":")
                if len(data) == 2:
                    key, v = data

                    if key == 'Size':
                        # print key ,v
                        if v.strip() != "No Module Installed":
                            # ram_item_to_dic['capacity'] =  v.split()[0].strip() # e.g split "1024 MB"
                            self.ram_data['capacity'] = v.split()[0].strip()  # e.g split "1024 MB"
                            item_ram_size = int(v.split()[0])
                            # print item_ram_size
                        else:
                            # ram_item_to_dic['capacity'] =  0
                            self.ram_data['capacity'] = 0

                    if key == 'Type':
                        # ram_item_to_dic['model'] =  v.strip()
                        self.ram_data['model'] =  v.strip()
                    if key == 'Manufacturer':
                        # ram_item_to_dic['manufactory'] =  v.strip()
                        self.ram_data['manufacturer'] =  v.strip()
                    if key == 'Serial Number':
                        # ram_item_to_dic['sn'] =  v.strip()
                        self.ram_data['sn'] =  v.strip()
                    if key == 'Asset Tag':
                        # ram_item_to_dic['asset_tag'] =  v.strip()
                        self.ram_data['asset_tag'] =  v.strip()
                    if key == 'Locator':
                        # ram_item_to_dic['slot'] =  v.strip()
                        self.ram_data['slot'] =  v.strip()

                        # if i.startswith("")
            if item_ram_size == 0:  # empty slot , need to report this
                pass
            else:
                # ram_list.append(ram_item_to_dic)
                self.data['ram'].append(dict(self.ram_data))

        # get total size(mb) of ram as well
        # raw_total_size = subprocess.check_output(" cat /proc/meminfo|grep MemTotal ",shell=True).split(":")
        # raw_total_size = commands.getoutput("cat /proc/meminfo|grep MemTotal ").split(":")
        # ram_data = {'ram':ram_list}
        # if len(raw_total_size) == 2:#correct
        #
        #     total_mb_size = int(raw_total_size[1].split()[0]) / 1024
        #     ram_data['ram_size'] =  total_mb_size
        #     print(ram_data)
        # print self.data['ram']

    def nic_info(self):
        # tmp_f = file(self'/tmp/bonding_nic').read()
        raw_data= subprocess.check_output("ifconfig -a",shell=True)
        # raw_data = commands.getoutput("ifconfig -a")

        raw_data= raw_data.split("\n")

        nic_dic = {}
        next_ip_line = False
        last_mac_addr = None
        for line in raw_data:
            if next_ip_line:
                # print last_mac_addr
                # print line #, last_mac_addr.strip()
                next_ip_line = False
                nic_name = last_mac_addr.split()[0]
                mac_addr = last_mac_addr.split("HWaddr")[1].strip()
                raw_ip_addr = line.split("inet addr:")
                raw_bcast = line.split("Bcast:")
                raw_netmask = line.split("Mask:")
                if len(raw_ip_addr) > 1:  # has addr
                    ip_addr = raw_ip_addr[1].split()[0]
                    network = raw_bcast[1].split()[0]
                    netmask = raw_netmask[1].split()[0]
                    # print(ip_addr,network,netmask)
                else:
                    ip_addr = None
                    network = None
                    netmask = None
                if mac_addr not in nic_dic:
                    nic_dic[mac_addr] = {'name': nic_name,
                                         'macaddress': mac_addr,
                                         'netmask': netmask,
                                         'network': network,
                                         'bonding': 0,
                                         'model': 'unknown',
                                         'ipaddress': ip_addr,
                                         }
                else:  # mac already exist , must be boding address
                    if '%s_bonding_addr' % mac_addr not in nic_dic:
                        random_mac_addr = '%s_bonding_addr' % mac_addr
                    else:
                        random_mac_addr = '%s_bonding_addr2' % mac_addr

                    nic_dic[random_mac_addr] = {'name': nic_name,
                                                'macaddress': random_mac_addr,
                                                'netmask': netmask,
                                                'network': network,
                                                'bonding': 1,
                                                'model': 'unknown',
                                                'ipaddress': ip_addr,
                                                }

            if "HWaddr" in line:
                # print line
                next_ip_line = True
                last_mac_addr = line

        # nic_list= []
        for k, v in nic_dic.items():
            # nic_list.append(v)
            self.data['nic'].append(v)

    def disk_info(self):
        obj = DiskPlugin()
        info = obj.linux()
        self.data['disk'] = info['physical_disk_driver']

    def collect(self):
        self.check_if_running_on_virtual_machine()
        if self.data['asset_type'] == 'server':
            self.sys_info()
            self.cpu_info()
            self.disk_info()
            self.ram_info()
            self.nic_info()
        else:
            self.sys_info()
            self.nic_info()

    def check_if_running_on_virtual_machine(self):
        # 判读linux系统是否运行在虚拟机上
        vm_list = ['Microsoft', 'VirtualBox', 'VMware', 'VirtualPC']
        for i in vm_list:
            raw_data = commands.getoutput("lspci |grep -i '%s'" % i)
            if len(raw_data) > 0:
                print ('This server is running on a virtual machine %s' % i)
                self.data['asset_type'] = 'virtual_machine'
                break
        # raw_data = subprocess.check_output("sudo dmidecode | grep 'Product Name' | head -1", shell=True)
        # raw_data = commands.getoutput("sudo dmidecode | grep 'Product Name' | head -1")
        # product_name = raw_data.split(':')[1]
        # return product_name



class DiskPlugin(object):

    def linux(self):
        result = {'physical_disk_driver':[]}

        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
            shell_command = "sudo %s/MegaCli  -PDList -aALL" % script_path
            output = commands.getstatusoutput(shell_command)
            result['physical_disk_driver'] = self.parse(output[1])
        except Exception as e:
            result['error'] = e
        return result

    def parse(self, content):
        """
        解析shell命令返回结果
        :param content: shell 命令结果
        :return:解析后的结果
        """
        response = []
        result = []
        for row_line in content.split("\n\n\n\n"):
            result.append(row_line)
        for item in result:
            temp_dict = {}
            for row in item.split('\n'):
                if not row.strip():
                    continue
                if len(row.split(':')) != 2:
                    continue
                key,value = row.split(':')
                name =self.mega_patter_match(key)
                if name:
                    if key == 'Raw Size':
                        raw_size = re.search('(\d+\.\d+)',value.strip())
                        if raw_size:

                            temp_dict[name] = raw_size.group()
                        else:
                            raw_size = '0'
                    else:
                        temp_dict[name] = value.strip()

            if temp_dict:
                response.append(temp_dict)
        return response

    def mega_patter_match(self,needle):
        grep_pattern = {'Slot':'slot', 'Raw Size':'capacity', 'Inquiry':'model', 'PD Type':'iface_type'}
        for key,value in grep_pattern.items():
            if needle.startswith(key):
                return value
        return False


# if __name__ == '__main__':
#     c = LinuxInfo()
#     print c.data
