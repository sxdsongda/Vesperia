#!/usr/bin/env python
# coding:utf-8

import os
Base_Dir = os.path.dirname(os.path.dirname(__file__))

Params = {
    'server': '192.168.1.5',
    'port': 8000,
    'request_timeout': 30,
    'log_file': '%s/logs/run_log' % Base_Dir,
    'auth': {
        'user': 'sxdsongda@hotmail.com',
        'token': 'abc'
    },
    'urls': {
        'asset_report': 'asset/report/'
    }
}

# 是否需要asset_id? 真实asset有自己的sn, 服务器完全可以通过sn确定这个asset是否存在
# asset_id是非必要的,虚拟机其实也是不需要的,虚拟机应该作为一个虚拟财产,不应该跟
# 实际asset搅合在一起,因为,虚拟机没有sn(即便有也不是唯一的),而sn是真实asset的一个必填字段,
# 而且是唯一的,不能重复,所以,虚拟机应该有自己单独的表结构,我们只关心,虚拟机的系统,虚拟机的管理IP
# 虚拟机的宿主以及业务线就已经足够了
#

