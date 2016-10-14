#!/usr/bin/env python
# coding:utf-8

# from django.core.wsgi import get_wsgi_application
# import os
# os.environ["DJANGO_SETTINGS_MODULE"] = "Vesperia.settings"
# application = get_wsgi_application()

import hashlib
import redis
from django.shortcuts import HttpResponse
import json
import time
from Vesperia import settings
import models
from django.core.exceptions import ObjectDoesNotExist


def json_date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.strftime("%Y-%m-%d")


def json_datetime_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.strftime("%Y-%m-%d %H:%M:%S")


def gen_hash_token(username, timestamp, token):
    md5_format_str = "%s\n%s\n%s" % (username, timestamp, token)
    obj = hashlib.md5()
    obj.update(md5_format_str)
    return obj.hexdigest()[10:17]


def token_required(func):
    def wrapper(*args, **kwargs):
        response = {'error': []}
        # for the view function report, the args should be request
        wsgi_request = args[0]
        # print wsgi_request.POST  this is the client's collected information of the server
        # print wsgi_request.GET  this contains the token info
        token_info = wsgi_request.GET
        username = token_info.get('user')
        token_md5_from_client = token_info.get('token')
        timestamp = token_info.get('timestamp')
        if not username or not token_md5_from_client or not timestamp:
            response['error'].append({"auth_failed": "This api require token authentication!"})
            return HttpResponse(json.dumps(response))   # 这里要联想到装饰器是相当于,report从wrapper下开始了,故这里可以用这个返回
        if abs(time.time() - int(timestamp)) > settings.TOKEN_TIMEOUT:
            # 这里要用服务器的时间减客户端的时间,是为了更高的安全性,防止在redis中的token数据expire之后,token被重新拿着用还认为继续仍然有效
            # 但是,这里有个新的问题出现,就是客户端的时间如果比服务器的快了120秒,那么客户端的这个token将会在240秒的时间内在这里被认为是没有过期的
            # 那么,如果缓存存在的时间少于240秒的话,就会出现漏洞,比如缓存存在时间也是120秒,那么如果客户端的数据被截获了就会留出120秒的被攻击的可能
            response['error'].append({"auth_failed": "Token expired!"})
        else:
            r = RedisHelper()
            if r.exists(username):
                try:
                    token_list_in_redis = r.lrange(username)
                    if token_md5_from_client in token_list_in_redis:
                        response['error'].append({"auth_failed": "Token expired!"})
                        return HttpResponse(json.dumps(response))
                except Exception as e:
                    print ('Redis key error, may have some problems on server\n%s' % e)
                    response['error'].append({"auth_failed": "Have problems on server"})
                    return HttpResponse(json.dumps(response))
                # 如果客户端自己连接到redis,是可以直接删key的,因此要给redis设置密码
            try:
                user_obj = models.UserProfile.objects.get(email=username)
                token_md5_from_server = gen_hash_token(username, timestamp, user_obj.token)
                if token_md5_from_client != token_md5_from_server:
                    response['error'].append({"auth_failed": "Invalid username or token_id"})
                    # 在操作数据库前防止了所有可能的错误,这个时候已经操作到了数据库,就不急于return了
                else:
                    # 这里验证通过了之后,应该将token做失效处理,可以将token存入redis或者文件,程序开头验证下在不在redis里面,然后即便数据被截获了,也已经失效了就很安全
                    r.rpush(username, token_md5_from_client, expire=300)
            except ObjectDoesNotExist:
                response['error'].append({"auth_failed": "Invalid username or token_id"})
        if response['error']:
            return HttpResponse(json.dumps(response))
        else:
            return func(*args, **kwargs)
    return wrapper


class RedisHelper(object):

    def __init__(self):
        self.__conn = redis.Redis(host=settings.RedisServer, port=settings.RedisPort, password=settings.RedisPass)

    def get(self, key):
        return self.__conn.get(key)

    def set(self, key, value, expire=0):
        self.__conn.set(key, value)
        if expire:
            self.__conn.expire(key, expire)

    def expire(self, key, value):
        self.__conn.expire(key, value)

    def exists(self, key):
        return self.__conn.exists(key)

    def type_of(self, key):
        return self.__conn.type(key)

    def rpush(self, key, value, expire=0):
        self.__conn.rpush(key, value)
        if expire:
            self.__conn.expire(key, expire)

    def lrange(self, key, start=0, end=-1):
        # set start = -1 if only want to get the last one
        return self.__conn.lrange(key, start, end)

    def key(self, pattern='*'):
        return self.__conn.keys(pattern)

    def set_json(self, key, value, expire=0):
        self.__conn.set(key, json.dumps(value))
        if expire:
            self.__conn.expire(key, expire)

    def get_json(self, key):
        # especially for a json decode data
        data = self.__conn.get(key)
        try:
            json_data = json.loads(data)
        except ValueError:
            return data
        else:
            return json_data

    def rpush_json(self, key, value):
        self.__conn.rpush(key, json.dumps(value))

    def lrange_json(self, key, start=0, end=-1):
        # set start = -1 if only want to get the last one
        data = self.__conn.lrange(key, start, end)
        try:
            json_data = []
            for i in data:
                json_data.append(json.loads(i))
            return json_data
        except ValueError:
            return data

    def del_key(self, key):
        self.__conn.delete(key)

# if __name__ == '__main__':
#     a = RedisHelper()
    # print a.type_of('a')
    # b = a.key()
    # for i in b:
    #     a.del_key(i)
    # a.sub_receive()
    # a.rpush('mylist2', 'wo')
    # a.rpush('mylist2', 'ni')
    # a.rpush('mylist2', 'ta')
    # print a.lrange('mylist2', start=-1)
