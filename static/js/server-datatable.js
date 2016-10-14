/**
 * Created by Daniel on 2016/8/18.
 */

$(function () {
    var $table = $('#asset-dataTable');
    var $wrapper = $('#div-table-container');
    console.log(window.location.pathname.split('/')[2])
    var asset_type = 'server';

    var _table = $table.dataTable($.extend(true, {}, CONSTANT.DATA_TABLE.DEFAULT_OPTION, {
        ajax: function (data, callback, settings) {
            //手动控制遮罩
            $wrapper.spinModal();
            //封装请求参数
            var params = serverManage.getQueryCondition(data);
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
        serverManage.fuzzySearch = true;

        //reload效果与draw(true)或者draw()类似,draw(false)则可在获取新数据的同时停留在当前页码,可自行试验
//      _table.ajax.reload();
//      _table.draw(false);
        _table.draw();
    });

    $("#btn-advanced-search").click(function(){
        serverManage.fuzzySearch = false;
        _table.draw();
    });

    $("tbody",$table).on("click","tr",function(event) {
        //行点击事件
        $(this).addClass("active").siblings().removeClass("active");
        //获取该行对应的数据
        var item = _table.row($(this).closest('tr')).data();
        serverManage.currentItem = item;
        serverManage.showItemDetail(item);
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
        serverManage.currentItem = item;
        serverManage.editItemInit(item);
    });

    $("#btn-asset-edit-confirm").click(function () {
        serverManage.batchConfig = false;
        var arrItemId = [];
        arrItemId.push(serverManage.currentItem);
        serverManage.editItemsSubmit(arrItemId)
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
        serverManage.batchConfig = true;
        serverManage.editItemsSubmit(arrItemId);
    });

});

var serverManage = {
    currentItem: null,
    fuzzySearch: true,
    batchConfig: false,
    getQueryCondition: function (data) {
        var param = {assetType: 'server'};
        var advancedSearchFormData = '';
         //组装排序参数
        if (data.order&&data.order.length&&data.order[0]) {
            switch (data.order[0].column) {
                case 1:
                    param.orderColumn = "id";
                    break;
                case 2:
                    param.orderColumn = "name";
                    break;
                case 3:
                    param.orderColumn = "sn";
                    break;
                case 4:
                    param.orderColumn = "idc__name";
                    break;
                case 5:
                    param.orderColumn = "business_unit__name";
                    break;
                case 6:
                    param.orderColumn = "admin__email";
                    break;
                default:
                    param.orderColumn = "id";
                    break;
            }
            param.orderDir = data.order[0].dir;
        }
        //组装查询参数
        param.fuzzySearch = serverManage.fuzzySearch;
        if (serverManage.fuzzySearch) {
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
        $("#idc-view").text(item.idc__name);
        $("#business-view").text(item.business_unit__name);
        $("#admin-view").text(item.admin__email);
        $("#server-model-view").text(item.server__model);
        $("#cpu-model-view").text(item.cpu__cpu_model);
        $("#cpu-count-view").text(item.cpu__cpu_count);
        $("#cpu-core-count-view").text(item.cpu__cpu_core_count);
        $("#manage-ip-view").text(item.manage_ip);
        $("#manufacturer-view").text(item.manufacturer__name);
        $("#trade-date-view").text(item.trade_date);
        $("#expire-date-view").text(item.expire_date);
        $("#price-view").text(item.price);
        $("#contract-view").text(item.contract__name);
        $("#ram-size-view").text(item.ram_size);
        $("#disk-size-view").text(item.disk_size);
        $("#tags-view").text(item.tags__name);
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
                var postData = {} ;
                var formData;
                if (serverManage.batchConfig){
                    formData = $("#batch-config-form").serialize();
                }
                else {
                    formData = $("#asset-edit-form").serialize();
                }
                postData.batchConfig = serverManage.batchConfig;
                postData.id = idList;
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
                                        errorProps += p + ": "+ error[p][i] + "\n"
                                    }
                                }
                            }  // 最后显示所有的属性
                            $.dialog.alert("修改失败。错误：\n" + errorProps)
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
    }
};

