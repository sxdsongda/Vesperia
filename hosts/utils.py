#!/usr/bin/env python
# coding:utf-8
from Vesperia import settings
import os
import random


def json_date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.strftime("%Y-%m-%d %T")


def uploaded_file_handle(user_id, file_list):
    random_sample = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz0123456789', 10))
    user_dir = '%s/%s' % (settings.FileUploadDir, user_id)
    random_dir = '%s/%s' % (user_dir, random_sample)
    upload_file_list = []
    if not os.path.isdir(user_dir):
        os.mkdir(user_dir)
    if not os.path.isdir(random_dir):
        os.mkdir(random_dir)

    # 这里需要说明下, 其实本来把随机数和user_id传回去就可以了,这样也不需要传回去列表,
    # 但是这里这样写的目的是为了,把实际传的文件记录到数据库中,而不是只记那个随机数目录,
    # 也许可以减少点以后审计查询的麻烦,因为上传的随机数文件夹有可能会被删掉,那被删掉了就怎么
    # 都不知道当时传的是什么东西了,这条记录也就废了,另外,有可能文件上传进来了,用户却不执行任务,
    # 存在的文件夹就是多余的,总是有可能有些原因让我们去清理这些文件的,但是清理后我还要知道以前
    # 分发过些什么文件的话,就必须要把每个文件名都写入数据库
    for f in file_list:
        print f.name
        upload_file = '%s/%s/%s' % (user_id, random_sample, f.name)
        upload_file_list.append(upload_file)
        with open('%s/%s' % (random_dir, f.name), 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    return upload_file_list


