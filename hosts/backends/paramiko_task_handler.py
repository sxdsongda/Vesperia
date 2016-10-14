#!/usr/bin/env python
# coding:utf-8

import paramiko, json, os, random
from hosts import models
from Vesperia import settings
from django.utils import timezone


def paramiko_ssh(task_id, bound_host, task_content):
    print ('going to run %s on %s' % (task_content, bound_host))
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 这里要用到异常处理,因为远程操作有可能出现各种问题,一旦出现了问题,就要抓住这个异常,
    # 然后把这个异常,作为task_result,存入数据库,并且设置result_status为failed
    try:
        if bound_host.host_user.auth_type == 'ssh-password':
            ssh.connect(
                hostname=bound_host.host.ip_addr,
                port=int(bound_host.host.port),
                username=bound_host.host_user.username,
                password=bound_host.host_user.password,
                timeout=5
            )
        elif bound_host.host_user.auth_type == 'ssh-key':
            key = paramiko.RSAKey.from_private_key_file(
                settings.RSA_PRIVATE_KEY_FILE
            )
            ssh.connect(
                hostname=bound_host.host.ip_addr,
                port=int(bound_host.host.port),
                username=bound_host.host_user.username,
                pkey=bound_host.host_user.key,
                # pkey=key,
                timeout=5
            )
        stdin, stdout, stderr = ssh.exec_command(task_content)
        cmd_result = stdout.read(), stderr.read()
        # 这样结果会是一个二元组('','failed') ('result',''), 但是如果只需要那个有效的部分
        # 可以有两种办法,一个是用join方法,把两段字符串拼起来, 另一个是用lambda函数,配合filter
        cmd_result = filter(lambda x: len(x) > 0, cmd_result)[0]
        result_status = 'success'
    except Exception as e:
        print ('\033[31;1m%s\033[0m' % e)
        cmd_result = e
        result_status = 'failed'
    # 找出这条记录,然后把内容更新,注意这里不要写成了创建一条新的记录
    task_detail_object = models.TaskLogDetail.objects.get(task_id=task_id, bound_host=bound_host)
    task_detail_object.result_content = cmd_result
    task_detail_object.result_status = result_status
    task_detail_object.date = timezone.now()
    task_detail_object.save()


def paramiko_sftp(task_id, task_type, bound_host, task_content):
    print ('going to transfer files with remote hosts')
    try:
        ip_addr = bound_host.host.ip_addr
        port = bound_host.host.port
        username = bound_host.host_user.username
        task_content = json.loads(task_content)
        remote_path = task_content['remote_path']
        result_content = ''

        t = paramiko.Transport(ip_addr, port)
        if bound_host.host_user.auth_type == 'ssh-password':
            password = bound_host.host_user.password
            t.connect(username=username, password=password)
        else:
            key = bound_host.host_user.key
            t.connect(username=username, pkey=key)

        sftp = paramiko.SFTPClient.from_transport(t)

        if task_type == 'file_send':
            upload_response = task_content['upload_response']
            for file_path in upload_response:
                file_to_send = os.path.join(settings.FileUploadDir, file_path)
                file_name = file_path.split('/')[-1]
                remote_file_path = os.path.join(remote_path, file_name)
                sftp.put(localpath=file_to_send, remotepath=remote_file_path)
            t.close()
            result_content = 'Successfully send files %s to remote host [%s]' % (upload_response, ip_addr)
        elif task_type == 'file_get':
            files = sftp.listdir(remote_path)
            host_id = bound_host.host.id
            user_dir = '%s/%s' % (settings.FileDownloadDir, host_id)
            random_sample = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz0123456789', 10))
            user_random_dir = '%s/%s' % (user_dir, random_sample)
            if not os.path.isdir(user_dir):
                os.mkdir(user_dir)
            if not os.path.isdir(user_random_dir):
                os.mkdir(user_random_dir)
            for f in files:
                remote_file = os.path.join(remote_path, f)
                local_file = os.path.join(user_random_dir, f)
                sftp.get(localpath=local_file, remotepath=remote_file)
            t.close()
            result_content = 'Successfully downloads files %s from remote host [%s] to %s/%s' % (files, ip_addr,
                                                                                                 host_id, random_sample)
        result_status = 'success'

    except Exception as e:
        print ('\033[31;1m%s\033[0m' % e)
        result_content = e
        result_status = 'failed'
    task_detail_object = models.TaskLogDetail.objects.get(task_id=task_id, bound_host=bound_host)
    task_detail_object.result_content = result_content
    task_detail_object.result_status = result_status
    task_detail_object.date = timezone.now()
    task_detail_object.save()
