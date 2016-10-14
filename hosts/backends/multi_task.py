#!/usr/bin/env python
# coding:utf-8

from django.core.wsgi import get_wsgi_application
from django.core.exceptions import ObjectDoesNotExist
import os, sys
import multiprocessing
from multiprocessing import Queue

BASE_DIR = "/".join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-2])
sys.path.append(BASE_DIR)

os.environ["DJANGO_SETTINGS_MODULE"] = "Vesperia.settings"
application = get_wsgi_application()

from hosts import models
import paramiko_task_handler
"""
The application object¶

The key concept of deploying with WSGI is the application callable which the application server uses to communicate with your code.
It’s commonly provided as an object named application in a Python module accessible to the server.

The startproject command creates a file <project_name>/wsgi.py that contains such an application callable.

It’s used both by Django’s development server and in production WSGI deployments.

WSGI servers obtain the path to the application callable from their configuration.
Django’s built-in server, namely the runserver command, reads it from the WSGI_APPLICATION setting.
By default, it’s set to <project_name>.wsgi.application, which points to the application callable in <project_name>/wsgi.py.

"""
# import django
# django.setup()  #allow outside scripts involve django db modules


def by_paramiko(task_id):
    try:
        task_obj = models.TaskLog.objects.get(pk=task_id)
        pool = multiprocessing.Pool(processes=5)
        processes = []
        if task_obj.task_type == 'multi_cmd':
            for bound_host in task_obj.bound_hosts.select_related():
                p = pool.apply_async(paramiko_task_handler.paramiko_ssh, [task_id, bound_host, task_obj.task_content])
                processes.append(p)
        elif task_obj.task_type in ('file_send', 'file_get'):
                # 这里虽然可以用else,但是明确指明是哪个类型范围内明显更好
            for bound_host in task_obj.bound_hosts.select_related():
                p = pool.apply_async(paramiko_task_handler.paramiko_sftp,
                                     [task_id, task_obj.task_type, bound_host, task_obj.task_content])
                processes.append(p)
        for p in processes:
            p.get(timeout=30)

        # pool.close()
        # pool.join()

    except ObjectDoesNotExist as e:
        sys.exit(e)


def by_ansible(task_id):
    pass


def by_saltstack(task_id):
    pass


if __name__ == '__main__':
    required_args = ['-task_id', '-run_type']
    for arg in required_args:
        if arg not in sys.argv:
            print 'argument [%s] is required' % arg
            sys.exit()
    if len(sys.argv) != 5:
        print '5 arguments needed, %s given' % len(sys.argv)
        sys.exit()
    else:
        task_id = sys.argv[sys.argv.index('-task_id') + 1]
        run_type = sys.argv[sys.argv.index('-run_type') + 1]

        if hasattr(__import__(__name__), run_type):
            func = getattr(__import__(__name__), run_type)
            func(task_id)
        else:
            sys.exit("Invalid run_type, only support [by_paramiko, by_ansible, by_saltstack]")
