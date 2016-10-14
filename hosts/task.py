#!/usr/bin/env python
# coding:utf-8
import models
import os
import json
import subprocess
from django.db import transaction
from backends import multi_task
from Vesperia import settings


class Task(object):

    def __init__(self, request):
        self.request = request
        self.task_type = request.POST.get('task_type')
        self.task_content = self.request.POST.get('task_content')
        self.selected_hosts = set(self.request.POST.getlist('selected_hosts[]'))  # 这里不用json直接获取列表就需要这样写

    def handle(self):
        if self.task_type:
            if hasattr(self, self.task_type):
                func = getattr(self, self.task_type)
                return func()
            else:
                raise TypeError

# 这里可以按照数据库里面每个任务的类型,单独建立一个方法来处理对应的任务,但是这里处理的任务的过程只有
# 1. 数据库建立任务  2. 数据库建立任务的详细日志  3.触发脚本(由于在脚本那里会从数据库里面取数据,所以自然会得到是要干什么,因此脚本也是可以根据任务类型去做相应的事,但正式因为如此,
# 脚本可以判断,所以脚本也是一个就行了)
# 无论任务类型是什么,都是这三步,而且可以写成全部相同,因此是可以把所有的任务写到一起的统一叫一个task_action的,但我这里还是保留了反射的方法,因为是为了扩展,如果以后有别的需求需要增加,可以很方便

    def multi_cmd(self):
        print ("going to run cmd")
        task_id, pid = self.task_action()
        return {'task_id': task_id, 'pid': pid}

    def file_send(self):
        print ('==================== going to send files to remote hosts ====================')
        task_id, pid = self.task_action()
        return {'task_id': task_id, 'pid': pid}

    def file_get(self):
        print ('==================== going to get files from remote hosts ====================')
        task_id, pid = self.task_action()
        return {'task_id': task_id, 'pid': pid}

    def get_task_result(self):
        task_id = self.request.GET.get('task_id')
        if task_id:
            task_detail_list = models.TaskLogDetail.objects.filter(
                task_id=task_id).select_related('task__user', 'bound_host__host')
            return list(task_detail_list.values(
                'id', 'bound_host__host__hostname', 'bound_host__host__ip_addr',
                'result_status', 'result_content', 'date', 'task__user__name', 'bound_host__host_user__username'
            ))

        # 虽然可以返回数据库对象给前端,但是前端是没办法直接解析对象的,所以需要返回对象的值, 用values方法
        # 而且还可以向values里面指定内容 *field的形式

    @transaction.atomic
    def task_action(self):

        # 在数据库中创建任务
        task_obj = models.TaskLog(
            task_type=self.task_type,
            user=self.request.user,
            task_content=self.task_content
        )
        # many to many 关系只能先save了之后才能手动添加
        task_obj.save()
        task_obj.bound_hosts.add(*self.selected_hosts)  # add方法只接受(1,2,3),现在要传处理([1,2,3]),在参数前加*
        # 在数据中创建任务详细日志记录
        for host_id in self.selected_hosts:
            task_detail_obj = models.TaskLogDetail(
                task=task_obj,
                bound_host_id=host_id,
                result_content='N/A',
            )
            task_detail_obj.save()
        # 手动去触发后台的multitask script
        p = subprocess.Popen([
            'python',
            settings.MultiTaskScript,
            '-task_id', str(task_obj.id),
            '-run_type', settings.MultiTaskRunType,
        ], preexec_fn=os.setsid)
        print ('--->pid:', p.pid)
        return task_obj.id, p.pid

