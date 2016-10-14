#!/usr/bin/env python
# coding:utf-8

import hashlib
import time


def gen_hash_token(username, token):
    timestamp = int(time.time())
    md5_format_str = "%s\n%s\n%s" % (username, timestamp, token)
    obj = hashlib.md5()
    obj.update(md5_format_str)
    return obj.hexdigest()[10:17], timestamp

if __name__ == '__main__':
    print gen_hash_token('daniel', 'abc')


