# coding:utf-8
from django.shortcuts import render, HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
import json
import re
from . import core, utils, models, filters, forms, asset_handle
from django.db import transaction
# Create your views here.


@login_required
def index(request):
    print (request.GET)
    asset_type = request.GET.get('asset_type')
    if asset_type:
        asset_list = models.Asset.objects.filter(asset_type=asset_type)
    # print ('request_path:', request.META.get('QUERY_STRING))
    else:
        asset_list = models.Asset.objects.all().select_related().order_by('-id')
    paginator = Paginator(asset_list, 2)
    page = request.GET.get('page')
    try:
        asset_list_with_page = paginator.page(page)
    except PageNotAnInteger:
        asset_list_with_page = paginator.page(1)
    except EmptyPage:
        asset_list_with_page = paginator.page(paginator.num_pages)
    # if asset_type:
    #     return render(request, 'assets/index.html', {'data_list': asset_list_with_page})
    return render(request, 'assets/index.html', {
        'data_list': asset_list_with_page
    })


@login_required
def index_v2(request):
    get_dict = {}
    for k in request.GET.keys():
        v = request.GET.getlist(k)
        if len(v) == 1:  # 这里是为了同时能够满足用\\隔开的情况a=b||c和原始的a=b&a=c
            if re.match('||', v[0]):
                v = v[0].split('||')
        get_dict[k] = v
    f = filters.AssetFilter(get_dict, queryset=models.Asset.objects.all().select_related().prefetch_related('tags'))
    paginator = Paginator(f.qs, 500)
    page = request.GET.get('page')
    try:
        asset_list_with_page = paginator.page(page)
    except PageNotAnInteger:
        asset_list_with_page = paginator.page(1)
    except EmptyPage:
        asset_list_with_page = paginator.page(paginator.num_pages)
    return render(request, 'assets/index_v2.html', {'filter': f, 'data_list': asset_list_with_page})


@csrf_exempt
@utils.token_required
def report(request):
    data = json.loads(request.POST.get('asset_data'))
    print data
    asset_handler = core.Asset(request)
    res = asset_handler.handle()
    print res

    return HttpResponse(json.dumps(res))


def approval(request):
    pass


@login_required
def asset_approval(request):
    if request.method == 'POST':
        if request.is_ajax():
            post_dic = request.POST
            return_data = {'success': True, 'error': {}}
            id_list = post_dic.getlist('id[]')
            if post_dic.get('Action') == 'Delete':
                for i in id_list:
                    try:
                        new_asset_obj = models.NewAssetApprovalZone.objects.get(id=i)
                        new_asset_obj.delete()
                    except ObjectDoesNotExist:
                        pass  # 如果有几个人同时删除同一个对象，则会出现不存在的情况，但是没必要去做成错误，直接pass
            elif post_dic.get('Action') == 'Approve':
                for i in id_list:
                    response = core.Asset.create_asset_from_approval_zone(i, request)
                    if response['error']:
                        err_dic = {}
                        for err in response['error']:
                            err_dic.update(err)
                        return_data['error'].update({i: err_dic})
            else:
                return_data['error'] = {u'未知操作': post_dic.get('Action')}
                return_data['success'] = False
            return HttpResponse(json.dumps(return_data))
        else:
            return HttpResponse('Bad Request')
    search_form = filters.AssetApprovalFilter()
    return render(request, 'assets/asset_approval.html', {'search_form': search_form})


@login_required
def idc_contract_tags(request):
    return render(request, 'assets/idc_contract_tags.html')


@login_required
def detail(request, asset_id):
    try:
        asset_obj = models.Asset.objects.get(id=asset_id)
        func_dic = {'server': server_detail, 'software': software_detail,
                    'storage': storage_detail, 'other': server_detail}
        if asset_obj.asset_type not in func_dic.keys():
            return HttpResponse(network_device_detail(request, asset_obj))
        else:
            return HttpResponse(func_dic.get(asset_obj.asset_type)(request, asset_obj))

    except ObjectDoesNotExist as e:
        return render(request, 'assets/asset_detail.html', {'error': e})


def server_detail(request, asset_obj):
    if request.method == 'POST':
        print request.POST
        form = forms.AssetServerUpdateForm(request.POST, instance=asset_obj)
        if form.is_valid():
            form.save()
    else:
        form = forms.AssetServerUpdateForm(instance=asset_obj)
    return render(request, 'assets/server_detail.html', {'asset_obj': asset_obj, 'form': form})


def storage_detail(request, asset_obj):
    if request.method == 'POST':
        form = forms.AssetStorageForm(request.POST, instance=asset_obj)
        second_form = forms.StorageForm(request.POST, instance=models.Storage.objects.get(asset=asset_obj))
        if form.is_valid() and second_form.is_valid():
            form.save()
            second_form.save()
    else:
        form = forms.AssetStorageForm(instance=asset_obj)
        second_form = forms.StorageForm(instance=models.Storage.objects.get(asset=asset_obj))
    return render(request, 'assets/storage_detail.html', {
        'asset_obj': asset_obj, 'form': form, 'second_form': second_form})


def network_device_detail(request, asset_obj):
    if request.method == 'POST':
        form = forms.AssetNetworkDeviceForm(request.POST, instance=asset_obj)
        second_form = forms.NetworkDeviceForm(request.POST, instance=models.NetworkDevice.objects.get(asset=asset_obj))
        if form.is_valid() and second_form.is_valid():
            form.save()
            second_form.save()
    else:
        form = forms.AssetNetworkDeviceForm(instance=asset_obj)
        second_form = forms.NetworkDeviceForm(instance=models.NetworkDevice.objects.get(asset=asset_obj))
    return render(request, 'assets/network_device_detail.html', {
        'asset_obj': asset_obj, 'form': form, 'second_form': second_form})


def software_detail(request, asset_obj):
    if request.method == 'POST':
        form = forms.AssetSoftwareForm(request.POST, instance=asset_obj)
        second_form = forms.SoftwareForm(request.POST, instance=models.Software.objects.get(asset=asset_obj))
        if form.is_valid() and second_form.is_valid():
            form.save()
            second_form.save()
    else:
        form = forms.AssetSoftwareForm(instance=asset_obj)
        second_form = forms.SoftwareForm(instance=models.Software.objects.get(asset=asset_obj))
    return render(request, 'assets/software_detail.html', {
        'asset_obj': asset_obj, 'form': form, 'second_form': second_form})


@login_required
@transaction.atomic
def virtual_machine(request):
    if request.method == 'POST':
        if request.is_ajax():
            post_dic = request.POST
            return_data = {'success': True, 'error': None}
            if post_dic.get('Delete') == 'true':
                id_list = post_dic.getlist('id[]')
                for i in id_list:
                    try:
                        vm_obj = models.VirtualMachine.objects.get(id=i)
                        vm_obj.delete()
                    except ObjectDoesNotExist:
                        pass
            elif post_dic.get('addItem') == 'true':
                virtual_machine_form = forms.VirtualMachineForm(post_dic)
                if virtual_machine_form.is_valid():
                    virtual_machine_form.save()
                else:
                    return_data['error'] = virtual_machine_form.errors
                    return_data['success'] = False
            else:
                vm_id = post_dic.getlist('id[]')[0]
                vm_obj = models.VirtualMachine.objects.get(id=vm_id)
                virtual_machine_form = forms.VirtualMachineForm(post_dic, instance=vm_obj)
                if virtual_machine_form.is_valid():
                    virtual_machine_form.save()
                else:
                    return_data['error'] = virtual_machine_form.errors
                    return_data['success'] = False
            return HttpResponse(json.dumps(return_data))
        else:
            return HttpResponse('Bad Request')
    search_form = filters.VirtualMachineFilter()
    virtual_machine_form = forms.VirtualMachineForm()
    return render(request, 'assets/virtual_machine.html', {
        'search_form': search_form, 'virtual_machine_form': virtual_machine_form})


@login_required
@transaction.atomic
def network_device(request):
    if request.method == 'POST':
        if request.is_ajax():
            post_dic = request.POST
            return_data = {'success': True, 'error': None}
            if post_dic.get('addItem') == 'true':
                asset_network_device_form = forms.AssetNetworkDeviceForm(post_dic)
                network_device_form = forms.NetworkDeviceNoDetailForm(post_dic)
                if asset_network_device_form.is_valid() and network_device_form.is_valid():
                    asset_obj = asset_network_device_form.save(commit=False)
                    asset_obj.asset_type = 'network_device'
                    asset_obj.save()
                    software_obj = network_device_form.save(commit=False)
                    software_obj.asset = asset_obj
                    software_obj.save()
                else:
                    error_dic = asset_network_device_form.errors
                    error_dic.update(network_device_form.errors)
                    return_data['error'] = error_dic
                    return_data['success'] = False
            else:
                asset_id = post_dic.getlist('id[]')[0]
                asset_obj = models.Asset.objects.get(id=asset_id)
                asset_network_device_form = forms.AssetNetworkDeviceForm(post_dic, instance=asset_obj)
                network_device_form = forms.NetworkDeviceNoDetailForm(
                    post_dic, instance=models.NetworkDevice.objects.get(asset=asset_obj))
                if network_device_form.is_valid() and asset_network_device_form.is_valid():
                    asset_network_device_form.save()
                    network_device_form.save()
                else:
                    error_dic = asset_network_device_form.errors
                    error_dic.update(network_device_form.errors)
                    return_data['error'] = error_dic
                    return_data['success'] = False
            return HttpResponse(json.dumps(return_data))
        else:
            return HttpResponse('Invalid Request')
    search_form = filters.NetworkDeviceFilter()
    asset_network_device_form = forms.AssetNetworkDeviceForm()
    network_device_form = forms.NetworkDeviceNoDetailForm()
    return render(request, 'assets/network_device.html', {
        'asset_network_device_form': asset_network_device_form, 'network_device_form': network_device_form,
        'search_form': search_form
    })


@login_required
@transaction.atomic
def storage(request):
    if request.method == 'POST':
        if request.is_ajax():
            post_dic = request.POST
            return_data = {'success': True, 'error': None}
            if post_dic.get('addItem') == 'true':
                asset_storage_form = forms.AssetStorageForm(post_dic)
                storage_form = forms.StorageForm(post_dic)
                if asset_storage_form.is_valid() and storage_form.is_valid():
                    asset_obj = asset_storage_form.save(commit=False)
                    asset_obj.asset_type = 'storage'
                    asset_obj.save()
                    storage_obj = storage_form.save(commit=False)
                    storage_obj.asset = asset_obj
                    storage_obj.save()
                else:
                    error_dic = asset_storage_form.errors
                    error_dic.update(storage_form.errors)
                    return_data['error'] = error_dic
                    return_data['success'] = False
            else:
                asset_id = post_dic.getlist('id[]')[0]
                asset_obj = models.Asset.objects.get(id=asset_id)
                asset_storage_form = forms.AssetStorageForm(post_dic, instance=asset_obj)
                storage_form = forms.StorageForm(post_dic, instance=models.Storage.objects.get(asset=asset_obj))
                if asset_storage_form.is_valid() and storage_form.is_valid():
                    asset_storage_form.save()
                    storage_form.save()
                else:
                    error_dic = asset_storage_form.errors
                    error_dic.update(storage_form.errors)
                    return_data['error'] = error_dic
                    return_data['success'] = False
            return HttpResponse(json.dumps(return_data))
        else:
            return HttpResponse('Bad Request')
    asset_storage_form = forms.AssetStorageForm()
    storage_form = forms.StorageForm()
    search_form = filters.StorageFilter()
    return render(request, 'assets/storage.html', {
        'asset_storage_form': asset_storage_form, 'storage_form': storage_form, 'search_form': search_form})


@login_required
@transaction.atomic
def software(request):
    if request.method == 'POST':
        if request.is_ajax():
            post_dic = request.POST
            return_data = {'success': True, 'error': None}
            if post_dic.get('addItem') == 'true':
                asset_software_form = forms.AssetSoftwareForm(post_dic)
                software_form = forms.SoftwareForm(post_dic)
                if asset_software_form.is_valid() and software_form.is_valid():
                    asset_obj = asset_software_form.save(commit=False)
                    asset_obj.asset_type = 'software'
                    asset_obj.save()
                    software_obj = software_form.save(commit=False)
                    software_obj.asset = asset_obj
                    software_obj.save()
                else:
                    error_dic = asset_software_form.errors
                    error_dic.update(software_form.errors)
                    return_data['error'] = error_dic
                    return_data['success'] = False
            else:
                asset_id = post_dic.getlist('id[]')[0]
                asset_obj = models.Asset.objects.get(id=asset_id)
                asset_software_form = forms.AssetSoftwareForm(post_dic, instance=asset_obj)
                software_form = forms.SoftwareForm(post_dic, instance=models.Software.objects.get(asset=asset_obj))
                if software_form.is_valid() and asset_software_form.is_valid():
                    software_form.save()
                    asset_software_form.save()
                else:
                    error_dic = asset_software_form.errors
                    error_dic.update(software_form.errors)
                    return_data['error'] = error_dic
                    return_data['success'] = False
            return HttpResponse(json.dumps(return_data))
        else:
            return HttpResponse('Invalid Request')
    search_form = filters.SoftwareFilter()
    asset_software_form = forms.AssetSoftwareForm(auto_id=False)
    software_form = forms.SoftwareForm(auto_id=False)
    return render(request, 'assets/software.html', {
        'asset_software_form': asset_software_form, 'software_form': software_form, 'search_form': search_form})


@login_required
def server(request):
    if request.method == 'POST':
        if request.is_ajax():
            post_dic = request.POST
            return_data = {'success': True, 'error': None}
            if post_dic.get('batchConfig') == 'true':
                id_list = post_dic.getlist('id[]')
                for i in id_list:
                    server_obj = models.Asset.objects.get(id=i)
                    form = forms.BatchServerConfigForm(post_dic, instance=server_obj)
                    if form.is_valid():
                        form.save()
                    else:
                        return_data['error'] = form.errors
                        return_data['success'] = False
                        break
            else:
                asset_id = post_dic.getlist('id[]')[0]
                form = forms.AssetServerUpdateForm(post_dic, instance=models.Asset.objects.get(id=asset_id))
                if form.is_valid():
                    form.save()
                else:
                    return_data['error'] = form.errors
                    return_data['success'] = False
            return HttpResponse(json.dumps(return_data))
        else:
            raise Http404('Invalid Request')
    config_form = forms.AssetServerUpdateForm(auto_id='%s-edit')
    batch_config_form = forms.BatchServerConfigForm(auto_id='%s-batch-edit')
    search_form = filters.ServerFilter()
    return render(request, 'assets/server.html', {
        'batch_config_form': batch_config_form, 'search_form': search_form, 'config_form': config_form})


@login_required
def get_asset_detail(request):
    asset_id = request.GET.get('asset_id')
    asset_type = request.GET.get('asset_type')
    a = {'k': 'v'}
    return HttpResponse(json.dumps(a))


@login_required
def ajax_get_asset_list(request):
    asset_type = request.GET.get('assetType')
    handler = asset_handle.AssetHandlerForDataTable(request, asset_type)
    data_dic = handler.handle()
    return HttpResponse(json.dumps(data_dic, default=utils.json_date_handler))


@login_required
def ajax_get_asset_approval_list(request):
    handler = asset_handle.AssetHandlerForDataTable(request, asset_type='asset_approval')
    data_dic = handler.handle()
    return HttpResponse(json.dumps(data_dic, default=utils.json_datetime_handler))


def event_log(request):
    return render(request, 'assets/event_log.html')