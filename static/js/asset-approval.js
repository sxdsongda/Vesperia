/**
 * Created by Daniel on 2016/9/6.
 */

$(function () {
    var $table = $('#asset-dataTable');
    var $wrapper = $('#div-table-container');

    var _table = $table.dataTable($.extend(true, {}, CONSTANT.DATA_TABLE.DEFAULT_OPTION, {
        ajax: function (data, callback, settings) {
            //手动控制遮罩
            $wrapper.spinModal();
            //封装请求参数
            var params = approvalManage.getQueryCondition(data);
            $.ajax({
                type: 'GET',
                url: '/asset/ajax_get_asset_approval_list',
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
        columns: TABLE_COLUMN['asset_approval'],
        "createdRow": function ( row, data, index ) {
            //行渲染回调,在这里可以对该行dom元素进行任何操作
            //给当前行加样式
            if (data.role) {
                $(row).addClass("info");
            }
            //给当前行某列加样式
            $('td', row).eq(7).addClass(data.status?"text-success":"text-error");
            var $btnApproval = $('<button type="button" class="btn btn-xs btn-default btn-approve">审批</button>');
            $('td', row).eq(-1).append(data.status == '未批准'? $btnApproval: '已审批');
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
        approvalManage.fuzzySearch = true;

        //reload效果与draw(true)或者draw()类似,draw(false)则可在获取新数据的同时停留在当前页码,可自行试验
//      _table.ajax.reload();
//      _table.draw(false);
        _table.draw();
    });

    $("#btn-advanced-search").click(function(){
        approvalManage.fuzzySearch = false;
        _table.draw();
    });

    $("tbody",$table).on("click","tr",function(event) {
        //行点击事件
        $(this).addClass("active").siblings().removeClass("active");
        //获取该行对应的数据
        var item = _table.row($(this).closest('tr')).data();
        approvalManage.showItemDetail(item);
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
    }).on("click",".td-checkbox",function(event) {
        //点击单元格即点击复选框
        !$(event.target).is(":checkbox") && $(":checkbox",this).trigger("click");
    });

    $("#toggle-advanced-search").click(function(){
        $("i",this).toggleClass("fa-angle-double-down fa-angle-double-up");
        // $("#div-advanced-search").slideToggle("fast");
    });

    // $("#btn-batch-approve").click(function () {
    //     //批量批准事件
    //     var arrItemId = [];
    //     $("tbody :checkbox:checked",$table).each(function() {
    //         var item = _table.row($(this).closest('tr')).data();
    //         arrItemId.push(item);
    //     });
    //     approvalManage.approvalItemsSubmit(arrItemId);
    // });

    $("#btn-approve").click(function () {
        //批准事件
        var arrItemId = [];
        var item = _table.row($(this).closest('tr')).data();
        arrItemId.push(item);
        approvalManage.approvalItemsSubmit(arrItemId);
    });


    
    $("#btn-batch-delete").click(function () {
        //批量删除事件
        var arrItemId = [];
        $("tbody :checkbox:checked",$table).each(function() {
            var item = _table.row($(this).closest('tr')).data();
            arrItemId.push(item);
        });
        approvalManage.delItemsSubmit(arrItemId);
    })
});

var approvalManage = {
    fuzzySearch: true,
    getQueryCondition: function (data) {
        var param = {};
        var advancedSearchFormData = '';
        //组装排序参数
        if (data.order&&data.order.length&&data.order[0]) {
            param.orderColumn = data.columns[data.order[0].column].data;
            param.orderDir = data.order[0].dir;
        }
        //组装查询参数
        param.fuzzySearch = approvalManage.fuzzySearch;
        if (approvalManage.fuzzySearch) {
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
        if (!item) {
            $("#asset-info-view .prop-value").text("");
            $("#asset-raw-data-view").text("");
            return;
        }
        $("#id-view").text(item.id);
        $("#sn-view").text(item.sn);
        $("#model-view").text(item.model);
        $("#asset-type-view").text(item.asset_type);
        $("#cpu-model-view").text(item.cpu_model);
        $("#cpu-count-view").text(item.cpu_count);
        $("#cpu-core-count-view").text(item.cpu_core_count);
        $("#ram-size-view").text(item.ram_size);
        $("#os-distribution-view").text(item.os_distribution);
        $("#os-release-view").text(item.os_release);
        $("#os-type-view").text(item.os_type);
        $("#manufacturer-view").text(item.manufacturer);
        $("#report-date-view").text(item.date);
        $("#approved-by-view").text(item.approved_by);
        $("#approved-date-view").text(item.approved_date);
        $("#status-view").text(item.status);

        $("#asset-raw-data-view").text(item.data)
    },
    approvalItemsSubmit:function (selectedItems) {
        var message;
        var csrf_token = $("input[name=csrfmiddlewaretoken]").val();
        if (selectedItems&&selectedItems.length) {
            var idList = [];
            if (selectedItems.length == 1) {
                message = "确定要批准id: '"+selectedItems[0].id+"' 吗?";
            }else{
                message = "确定要批准选中的"+selectedItems.length+"项记录吗?";
            }
            for (var i=0; i<selectedItems.length; i++){
                idList.push(selectedItems[i].id
                )}
            $.dialog.confirm(message, function(){
                var postData = {id: idList, csrfmiddlewaretoken: csrf_token, Action: 'Approve'} ;
                $.ajax({
                    type: 'POST',
                    url: '',
                    cache: false,
                    data: $.param(postData),
                    data_type: 'json',
                    success: function(result) {
                        $.dialog.tips('已提交审批操作');
                        result = JSON.parse(result);
                        var errorProps = "" ;
                        var error = result.error;
                        if(result.success == true&&!result.error){
                            $.dialog.tips('审批成功');
                        }
                        else if (result.success == true&&result.error){
                            for (var p in error){
                                if (error.hasOwnProperty(p)){
                                    for (var i in error[p]){
                                        if (error[p].hasOwnProperty(i)){
                                            errorProps += p + ": "+ i + error[p][i] + "<br>"
                                        }
                                    }
                                }
                            }  // 最后显示所有的属性
                            $.dialog.alert("审批出现问题：<br>" + errorProps)
                        }
                        else {
                            for (var q in error){
                                if (error.hasOwnProperty(q)){
                                    for (var j=0; i<error[q].length; i++){
                                        errorProps += q + ": "+ error[q][j] + "<br>"
                                    }
                                }
                            }  // 最后显示所有的属性
                            $.dialog.alert("审批失败：<br>" + errorProps)

                        }
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        $.dialog.alert("提交失败");
                    }
                });
            });
        }else{
            $.dialog.tips('请先选中要批准的行');
        }
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
                var postData = {Action: 'Delete', id: idList, csrfmiddlewaretoken: csrf_token} ;
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
                            $.dialog.alert("删除出现错误：<br>" + errorProps)
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
