#!/usr/bin/env python
# coding:utf-8


def linux_sysinfo():
    from .Linux import sysinfo
    data = sysinfo.collect()
    return data


def windows_sysinfo():
    from .Windows import sysinfo
    data = sysinfo.collect()
    return data

