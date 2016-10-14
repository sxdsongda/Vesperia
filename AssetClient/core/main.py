#!/usr/bin/env python
# coding:utf-8

from conf import settings
from plugins import plugin_api
import platform
import datetime
import sys
import json
import urllib, urllib2
import codecs
from utils import api_token


class AssetClient(object):
    def __init__(self):
        self.platform = platform.system()

    def start(self):
        self.report_data()

    def collect_info(self):
        try:
            func = getattr(self, self.platform)
            info_data = func()
            return info_data
        except AttributeError as e:
            sys.exit("Error:AssetClient doesn't support os [%s]" % e)

    def Linux(self):
        data = plugin_api.linux_sysinfo()
        return data

    def Windows(self):
        data = plugin_api.windows_sysinfo()
        return data

    def report_data(self):
        asset_info = self.collect_info()
        server_ip = settings.Params['server']
        port = settings.Params['port']
        path = settings.Params['urls']['asset_report']
        url = "http://%s:%s/%s" % (server_ip, port, path)
        response = self.__submit_data(asset_info, url)
        self.log_record(response)
        print response

    def __attach_token_to_url(self, url_str):
        """
        这个私有方法是为了给url加上token信息,并且加上和服务器约定好的加密算法所必须的字段和相应的数据
        :param url_str:
        :return:  处理好的新url
        """
        user = settings.Params['auth']['user']
        token_id = settings.Params['auth']['token']
        md5_token, timestamp = api_token.gen_hash_token(username=user, token=token_id)
        url_arg_str = "user=%s&timestamp=%s&token=%s" % (user, timestamp, md5_token)
        if "?" in url_str:
            new_url = url_str + "&" + url_arg_str
        else:
            new_url = url_str + "?" + url_arg_str
        return new_url

    def __submit_data(self, data, url):
        try:
            url = self.__attach_token_to_url(url)
            print 'report to url:\n', url
            post_dic = {'asset_data': json.dumps(data)}
            data_encode = urllib.urlencode(post_dic)
            # 要想在服务器端用request.POST.get(),这里要用urlencode
            req = urllib2.Request(url=url, data=data_encode)
            res_data = urllib2.urlopen(req, timeout=settings.Params['request_timeout'])
            callback = res_data.read()

            callback = json.loads(callback)
            return callback
        except Exception as e:
            sys.exit("\033[31;1m%s\033[0m" % e)

    def log_record(self, log):
        f = codecs.open(settings.Params['log_file'], 'ab+', 'utf-8')
        """
        {'info':[{'a':'A'},{'b':'B'}]}
        {'error':[{'a':'A'},{'b':'B'}]}
        {'warning':[{'a':'A'},{'b':'B'}]}
        """

        if type(log) is dict:

            format_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for key, val in log.items():
                if type(val) is list:
                    for i in val:
                        for k, v in i.items():
                            log_format = "%s\t%s\t%s\t%s\n" % (format_time, key.upper(), k, v)
                            f.write(log_format)
                else:
                    raise TypeError
        f.close()
