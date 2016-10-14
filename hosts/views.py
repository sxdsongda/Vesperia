# coding:utf-8
from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from . import task, utils
import json

# Create your views here.


@login_required
def index(request):
    return render(request, 'hosts/index.html')


@login_required
def multi_cmd(request):
    return render(request, 'hosts/multi_cmd.html')


@login_required
def multi_file_transfer(request):
    return render(request, 'hosts/multi_file_transfer.html')


@login_required
def submit_task(request):
    task_obj = task.Task(request)
    res = task_obj.handle()
    return HttpResponse(json.dumps(res))


@login_required
def get_task_result(request):
    task_obj = task.Task(request)
    res = task_obj.get_task_result()
    return HttpResponse(json.dumps(res, default=utils.json_date_handler))  # json dumps python datetime.datetime.now


@csrf_exempt
@login_required
def file_upload(request):
    uploaded_files = request.FILES.getlist('file')   # 由于是同步批量上传,所以这里要用getlist,不能直接靠request.FILES['file']获得
    random_dir_dic = utils.uploaded_file_handle(request.user.id, uploaded_files)
    return HttpResponse(json.dumps(random_dir_dic))


@login_required
def mission_plan(request):
    return render(request, 'hosts/mission.html')


@login_required
def audit(request):
    return render(request, 'hosts/audit.html')