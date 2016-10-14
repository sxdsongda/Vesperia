/**
 * Created by Daniel on 2016/8/31.
 */

/*
这个是用于资产配置下的所有页面
*/

$(function () {
    var $table = $('#asset-dataTable');
    var $wrapper = $('#div-table-container');
    var asset_type = window.location.pathname.split('/')[2];
    assetManage.assetType = asset_type;
    
    var _table = $table.dataTable($.extend(true, {}, CONSTANT.DATA_TABLE.DEFAULT_OPTION, {
        ajax: function (data, callback, settings) {
            //手动控制遮罩
            $wrapper.spinModal();
            //封装请求参数
            var params = assetManage.getQueryCondition(data);
            $.ajax({
                type: 'GET',
                url: '/asset/ajax_get_asset_list',
                cache: false,
                data: params,
                data_type: 'json',
                success: function(result) {
                    result = JSON.parse(result);
                    //setTimeout仅为测试延迟效果
                    setTimeout(function(){
                        //异常判断与处理
                        if (result.errorCode) {
                            $.dialog.alert("查询失败。错误码："+result.errorCode);
                            return;
                        }
                        //封装返回数据，这里仅演示了修改属性名
                        var returnData = {};
                        returnData.draw = result.draw;//这里直接自行返回了draw计数器,应该由后台返回
                        returnData.recordsTotal = result.recordsTotal;
                        returnData.recordsFiltered = result.recordsFiltered;//后台不实现过滤功能，每次查询均视作全部结果
                        returnData.data = result.data;
                        //关闭遮罩
                        $wrapper.spinModal(false);
                        //调用DataTables提供的callback方法，代表数据已封装完成并传回DataTables进行渲染
                        //此时的数据需确保正确无误，异常判断应在执行此回调前自行处理完毕
                        callback(returnData);
                    },200);
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    $.dialog.alert("查询失败");
                    $wrapper.spinModal(false);
                }
            });
        },
        columns: TABLE_COLUMN[asset_type],
        "createdRow": function ( row, data, index ) {
            //行渲染回调,在这里可以对该行dom元素进行任何操作
            //给当前行加样式
            if (data.role) {
                $(row).addClass("info");
            }
            //不使用render，改用jquery文档操作呈现单元格
            var $btnEdit = $('<button type="button" class="btn btn-xs btn-default btn-edit">修改</button>');
            $('td', row).eq(-1).append($btnEdit);
        },
        "drawCallback": function( settings ) {
            //渲染完毕后的回调
            //清空全选状态
            $(":checkbox[name='check-all']").prop('checked', false);
            //默认选中第一行
            $("tbody tr", $table).eq(0).click();
        }
    })).api();
    $("#btn-simple-search").click(function(){
        assetManage.fuzzySearch = true;

        //reload效果与draw(true)或者draw()类似,draw(false)则可在获取新数据的同时停留在当前页码,可自行试验
//      _table.ajax.reload();
//      _table.draw(false);
        _table.draw();
    });

    $("#btn-advanced-search").click(function(){
        assetManage.fuzzySearch = false;
        _table.draw();
    });

    $("tbody",$table).on("click","tr",function(event) {
        //行点击事件
        $(this).addClass("active").siblings().removeClass("active");
        //获取该行对应的数据
        var item = _table.row($(this).closest('tr')).data();
        assetManage.currentItem = item;
        assetManage.showItemDetail(item);
        $("#panel-title").text('资产详情')
    });

    $table.on("change",":checkbox",function() {
        var checkbox = $("tbody :checkbox",$table);
        if ($(this).is("[name='check-all']")) {
            //全选
            $(":checkbox",$table).prop("checked",$(this).prop("checked"));
        }else{
            //一般复选
            $(":checkbox[name='check-all']",$table).prop('checked', checkbox.length == checkbox.filter(':checked').length);
        }
        if(!checkbox.filter(':checked').length){
            $("#btn-batch-config-confirm").attr('disabled', true)
        }
        else {
            $("#btn-batch-config-confirm").attr('disabled', false)
        }
    }).on("click",".td-checkbox",function(event) {
        //点击单元格即点击复选框
        !$(event.target).is(":checkbox") && $(":checkbox",this).trigger("click");
    }).on("click",".btn-edit",function() {
        //点击编辑按钮
        var item = _table.row($(this).closest('tr')).data();
        $(this).closest('tr').addClass("active").siblings().removeClass("active");
        assetManage.currentItem = item;
        assetManage.editItemInit(item);
    }).on("click", ".btn-del", function () {
        //点击删除按钮
        var item = _table.row($(this).closest('tr')).data();
        $(this).closest('tr').addClass("active").siblings().removeClass("active");
        assetManage.currentItem = item;
        assetManage.delItemsSubmit([item]);
    });

    $("#btn-asset-edit-confirm").click(function () {
        assetManage.batchConfig = false;
        var arrItemId = [];
        arrItemId.push(assetManage.currentItem);
        assetManage.editItemsSubmit(arrItemId)
    });

    $("#toggle-advanced-search").click(function(){
        $("i",this).toggleClass("fa-angle-double-down fa-angle-double-up");
        // $("#div-advanced-search").slideToggle("fast");
    });

    $("#btn-batch-config-toggle").click(function () {
        $("i",this).toggleClass("fa-angle-double-down fa-angle-double-up");
        $("#info-panel-body-container").collapse('toggle');
    });

    $("#btn-batch-config-confirm").click(function () {
        //批量修改事件
        var arrItemId = [];
        $("tbody :checkbox:checked",$table).each(function() {
            var item = _table.row($(this).closest('tr')).data();
            arrItemId.push(item);
        });
        assetManage.batchConfig = true;
        assetManage.editItemsSubmit(arrItemId);
    });
    $("#btn-add").click(function () {
        assetManage.addItemInit();
    });
    $("#btn-asset-add-confirm").click(function () {
        assetManage.addItemSubmit();
    });
    $("#btn-batch-delete").click(function () {
        //批量删除事件
        var arrItemId = [];
        $("tbody :checkbox:checked",$table).each(function() {
            var item = _table.row($(this).closest('tr')).data();
            arrItemId.push(item);
        });
        assetManage.delItemsSubmit(arrItemId);
    })

});

var assetManage = {
    currentItem: null,
    fuzzySearch: true,
    batchConfig: false,
    assetType: null,
    getQueryCondition: function (data) {
        var param = {assetType: assetManage.assetType};
        var advancedSearchFormData = '';
        //组装排序参数
        if (data.order&&data.order.length&&data.order[0]) {
            param.orderColumn = data.columns[data.order[0].column].data;
            param.orderDir = data.order[0].dir;
        }
        //组装查询参数
        param.fuzzySearch = assetManage.fuzzySearch;
        if (assetManage.fuzzySearch) {
            param.fuzzy = $("#fuzzy-search").val();
        }else{
            advancedSearchFormData += '&' + $("#advanced-search-form").serialize()
        }
        //组装分页参数
        param.startIndex = data.start;
        param.pageSize = data.length;
        //draw
        param.draw = data.draw;
        return $.param(param) + advancedSearchFormData
    },
    showItemDetail: function (item) {
        $("#asset-info-view").show().siblings(".block-content").hide();
        if (!item) {
            $("#asset-info-view .prop-value").text("");
            return;
        }
        $("#id-view").text(item.id);
        $("#name-view").text(item.name);
        $("#sn-view").text(item.sn);
        $("#admin-view").text(item.admin__email);
        $("#manage-ip-view").text(item.manage_ip);
        $("#idc-view").text(item.idc__name);
        $("#business-view").text(item.business_unit__name);
        $("#manufacturer-view").text(item.manufacturer__name);
        $("#trade-date-view").text(item.trade_date);
        $("#expire-date-view").text(item.expire_date);
        $("#price-view").text(item.price);
        $("#contract-view").text(item.contract__name);
        $("#tags-view").text(item.tags__name);
        $("#nic-ip-view").text(item.nic_ip)
        // 专属server部分
        $("#server-model-view").text(item.server__model);
        $("#cpu-model-view").text(item.cpu__cpu_model);
        $("#cpu-count-view").text(item.cpu__cpu_count);
        $("#cpu-core-count-view").text(item.cpu__cpu_core_count);
        $("#ram-size-view").text(item.ram_size);
        $("#disk-size-view").text(item.disk_size);
        //专属software部分
        $("#software-type-view").text(item.software__software_type);
        $("#version-view").text(item.version);
        $("#language-view").text(item.software__language);
        $("#platform-view").text(item.software__platform);
        //专属network_device部分
        $("#mac-view").text(item.macaddress);
        $("#vlan-ip-view").text(item.vlan_ip);
        $("#intranet-ip-view").text(item.intranet_ip);
        $("#firmware-view").text(item.firmware);
        $("#port-num-view").text(item.port_num);
        $("#device-model-view").text(item.model);
        $("#device-type-view").text(item.networkdevice__device_type);
        //专属storage部分
        $("#storage-type-view").text(item.storage__storage_type);
        $("#storage-model-view").text(item.model);
        $("#capacity-view").text(item.storage__capacity);
        $("#interface-type-view").text(item.storage__interface_type);
        //专属virtual machine部分
        $("#vm-type-view").text(item.vm_type);
        $("#vm-mac-view").text(item.macaddress);
        $("#vm-manage-ip-view").text(item.manage_ip);
        $("#vm-os-distribution-view").text(item.os_distribution);
        $("#vm-os-arch-view").text(item.os_arch);
        $("#vm-os-release-view").text(item.os_release);
        $("#vm-os-type-view").text(item.os_type);
        $("#host-admin-view").text(item.host__admin__email);
        $("#host-tags-view").text(item.host__tags__name);
        $("#host-idc-view").text(item.host__idc__name);
        $("#host-business-view").text(item.host__business_unit__name);
        $("#host-name-view").text(item.host__name);
    },
    editItemsSubmit: function (selectedItems) {
        var message;
        if (selectedItems&&selectedItems.length) {
            var idList = [];
            if (selectedItems.length == 1) {
                message = "确定要修改 '"+selectedItems[0].name+"' 吗?";
            }else{
                message = "确定要修改选中的"+selectedItems.length+"项记录吗?";
            }
            for (var i=0; i<selectedItems.length; i++){
                idList.push(selectedItems[i].id
                )}
            $.dialog.confirm(message, function(){
                var postData = {batchConfig: assetManage.batchConfig, id: idList} ;
                var formData;
                if (assetManage.batchConfig){
                    formData = $("#batch-config-form").serialize();
                }
                else {
                    formData = $("#asset-edit-form").serialize();
                }
                $.ajax({
                    type: 'POST',
                    url: '',
                    cache: false,
                    data: formData + '&' + $.param(postData),
                    data_type: 'json',
                    success: function(result) {
                        $.dialog.tips('已提交修改操作');
                        result = JSON.parse(result);
                        if(result.success == true){
                            $.dialog.tips('修改成功');
                        }
                        else {
                            var errorProps = "" ;
                            var error = result.error;
                            for (var p in error){
                                if (error.hasOwnProperty(p)){
                                    for (var i=0; i<error[p].length; i++){
                                        errorProps += p + ": "+ error[p][i] + "<br>"
                                    }
                                }
                            }  // 最后显示所有的属性
                            $.dialog.alert("修改失败。错误：<br>" + errorProps)
                        }
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        $.dialog.alert("提交失败");
                    }
                });
            });
        }else{
            $.dialog.tips('请先选中要操作的行');
        }
    },
    editItemInit: function (item) {
        if(!item){
            return;
        }
        $("#asset-edit-view").show().siblings('.block-content').hide();
        $("#panel-title").text('修改资产： ID：'+ item.id + ' SN:'+ item.sn);
        $("#asset-edit-form").loadJson(item);
    },
    addItemInit: function () {
        $("#asset-add-view").show().siblings('.block-content').hide();
        $("#panel-title").text('新增资产')
    },
    addItemSubmit: function () {
        var message = '确定要新增一个资产吗？';
        var postData = {addItem: true};
        var formData = $("#asset-add-form").serialize();
        $.dialog.confirm(message, function () {
            $.ajax({
                type: 'POST',
                url: '',
                cache: false,
                data: formData + '&' + $.param(postData),
                data_type: 'json',
                success: function (result) {
                    $.dialog.tips('已提交新增资产请求');
                    result = JSON.parse(result);
                    if(result.success == true){
                        $.dialog.tips('新增成功');
                    }
                    else {
                        var errorProps = "" ;
                        var error = result.error;
                        for (var p in error){
                            if (error.hasOwnProperty(p)){
                                for (var i=0; i<error[p].length; i++){
                                    errorProps += p + ": "+ error[p][i] + "<br>"
                                }
                            }
                        }  // 最后显示所有的属性
                        $.dialog.alert("操作失败。错误：<br>" + errorProps)
                    }
                }
            })
        })
    },
    delItemsSubmit:function (selectedItems) {
        var message;
        var csrf_token = $("input[name=csrfmiddlewaretoken]").val();
        if (selectedItems&&selectedItems.length) {
            var idList = [];
            if (selectedItems.length == 1) {
                message = "确定要删除 '"+selectedItems[0].name+"' 吗?";
            }else{
                message = "确定要删除选中的"+selectedItems.length+"项记录吗?";
            }
            for (var i=0; i<selectedItems.length; i++){
                idList.push(selectedItems[i].id
                )}
            $.dialog.confirm(message, function(){
                var postData = {Delete: true, id: idList, csrfmiddlewaretoken: csrf_token} ;
                $.ajax({
                    type: 'POST',
                    url: '',
                    cache: false,
                    data: $.param(postData),
                    data_type: 'json',
                    success: function(result) {
                        $.dialog.tips('已提交删除操作');
                        result = JSON.parse(result);
                        if(result.success == true){
                            $.dialog.tips('删除成功');
                        }
                        else {
                            var errorProps = "" ;
                            var error = result.error;
                            for (var p in error){
                                if (error.hasOwnProperty(p)){
                                    for (var i=0; i<error[p].length; i++){
                                        errorProps += p + ": "+ error[p][i] + "<br>"
                                    }
                                }
                            }  // 最后显示所有的属性
                            $.dialog.alert("删除失败。错误：<br>" + errorProps)
                        }
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        $.dialog.alert("提交失败");
                    }
                });
            });
        }else{
            $.dialog.tips('请先选中要删除的行');
        }
    }
};

