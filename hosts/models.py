# coding: utf-8
from __future__ import unicode_literals

from django.db import models
from MyAuth.models import UserProfile

# Create your models here.


class Host(models.Model):
    hostname = models.CharField(max_length=64, unique=True)
    ip_addr = models.GenericIPAddressField(unique=True)
    port = models.IntegerField(default=22)
    system_type_choices = (
        ('linux', "LINUX"),
        ('win32', "Windows")
    )
    system_type = models.CharField(choices=system_type_choices, max_length=32, default='linux')
    enabled = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)
    idc = models.ForeignKey('IDC')

    def __unicode__(self):
        return self.hostname

    class Meta:
        verbose_name = u'主机列表'
        verbose_name_plural = u'主机列表'


class IDC(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __unicode__(self):
        return self.name


class HostGroup(models.Model):
    name = models.CharField(max_length=64, unique=True)
    staffs = models.ManyToManyField(UserProfile)
    bound_hosts = models.ManyToManyField('BindHostToHostUser')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'主机组'
        verbose_name_plural = u'主机组'


class HostUser(models.Model):
    auth_type_choice = (
        ('ssh-password', 'SSH/PASSWORD'),
        ('ssh-key', 'SSH/KEY'),
    )
    auth_type = models.CharField(choices=auth_type_choice, max_length=32, default='ssh-password')
    username = models.CharField(max_length=64)
    password = models.CharField(max_length=64)
    key = models.CharField(max_length=128, blank=True, null=True)
    status = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s(%s)" % (self.username, self.auth_type)

    class Meta:
        unique_together = ('auth_type', 'username', 'password')
        verbose_name = u'远程主机用户'
        verbose_name_plural = u'远程主机用户'


class BindHostToHostUser(models.Model):
    host = models.ForeignKey('Host')
    host_user = models.ForeignKey('HostUser')

    def __unicode__(self):
        return '%s(%s)' % (self.host.hostname, self.host_user.username)

    class Meta:
        unique_together = ('host', 'host_user')
        verbose_name = u'主机与远程用户绑定关系'
        verbose_name_plural = u'主机与远程用户绑定关系'


class TaskLog(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    expire_time = models.IntegerField(default=30)
    task_type_choice = (
        ('multi_cmd', 'Multi_cmd'),
        ('file_send', '传送文件'),
        ('file_get', '下载文件'),
    )
    task_type = models.CharField(choices=task_type_choice, max_length=32)
    task_pid = models.IntegerField(default=0)
    task_content = models.TextField()
    user = models.ForeignKey(UserProfile)
    bound_hosts = models.ManyToManyField('BindHostToHostUser')
    note = models.TextField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return '%s::%s' % (self.user.name, self.task_type)

    class Meta:
        verbose_name = u'批量任务'
        verbose_name_plural = u'批量任务'


class TaskLogDetail(models.Model):
    task = models.ForeignKey('TaskLog')
    bound_host = models.ForeignKey('BindHostToHostUser')
    date = models.DateTimeField(auto_now_add=True)
    result_content = models.TextField()
    result_status_choices = (
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('unknown', 'Unknown'),
    )
    result_status = models.CharField(choices=result_status_choices, max_length=32, default='unknown')
    note = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return 'child of:%s host:%s' % (self.task.id, self.bound_host.host.ip_addr)

    class Meta:
        verbose_name = u'批量任务日志'
        verbose_name_plural = u'批量任务日志'
