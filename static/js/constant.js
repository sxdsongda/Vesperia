/**
 * Created by Daniel on 2016/8/17.
 */

var CONSTANT = {
    DATA_TABLE: {
        DEFAULT_OPTION: {
            language: {
                "sProcessing": "处理中...",
                "sLengthMenu": "显示 _MENU_ 项结果",
                "sZeroRecords": "没有匹配结果",
                "sInfo": "显示第 _START_ 至 _END_ 项结果，共 _TOTAL_ 项",
                "sInfoEmpty": "显示第 0 至 0 项结果，共 0 项",
                "sInfoFiltered": "(由 _MAX_ 项结果过滤)",
                "sInfoPostFix": "",
                "sSearch": "搜索:",
                "sUrl": "",
                "sEmptyTable": "表中数据为空",
                "sLoadingRecords": "载入中...",
                "sInfoThousands": ",",
                "oPaginate": {
                    "sFirst": "首页",
                    "sPrevious": "上页",
                    "sNext": "下页",
                    "sLast": "末页"
                },
                "oAria": {
                    "sSortAscending": ": 以升序排列此列",
                    "sSortDescending": ": 以降序排列此列"
                }
            },
            autoWidth: false,   //禁用自动调整列宽
            stripeClasses: ["odd", "even"],//为奇偶行加上样式，兼容不支持CSS伪类的场合
            order: [],          //取消默认排序查询,否则复选框一列会出现小箭头
            processing: false,  //隐藏加载提示,自行处理
            serverSide: true,   //启用服务器端分页
            searching: false    //禁用原生搜索
        },
        COLUMN: {
            CHECKBOX: { //复选框单元格
                className: "td-checkbox",
                orderable: false,
                width: "18px",
                data: null,
                render: function (data, type, row, meta) { //会有一个点击单元格即点击复选框的事件，所以这里label不写for
                    return '<input type="checkbox" class="solo-checkbox" ><label></label>';
                }
            },
            OPERATION: {
                className : "td-operation",
                data: null,
                defaultContent:"",
                orderable : false,
                width : "60px"
            },
            ID_LINK: {
                className: 'td-link',
                data: 'id',
                width: '20px',
                render: function (data, type, row, meta) {
                    return '<a href="/asset/'+ data +'">' + data + '</a>'
                }
            }
        },
        RENDER: {   //常用render可以抽取出来，如日期时间、头像等
            ELLIPSIS: function (data, type, row, meta) {
                data = data||"";
                return '<span title="' + data + '">' + data + '</span>';
            }
        }
    }
};

var TABLE_COLUMN = {
    server: [
        CONSTANT.DATA_TABLE.COLUMN.CHECKBOX,
        CONSTANT.DATA_TABLE.COLUMN.ID_LINK,
        {data: 'name', width: '100px'},
        {data: 'sn', width: '150px'},
        {data: 'idc__name'},
        {data: 'business_unit__name'},
        {data: 'admin__email'},
        {data: 'manage_ip'},
        {data: 'tags__name', orderable: false, width: '200px'},
        CONSTANT.DATA_TABLE.COLUMN.OPERATION
    ],
    software: [
        CONSTANT.DATA_TABLE.COLUMN.CHECKBOX,
        CONSTANT.DATA_TABLE.COLUMN.ID_LINK,
        {data: 'name', width: '100px'},
        {data: 'sn', width: '150px'},
        {data: 'software__software_type'},
        {data: 'version', orderable: false},
        {data: 'software__platform'},
        {data: 'software__language'},
        {data: 'admin__email'},
        CONSTANT.DATA_TABLE.COLUMN.OPERATION
    ],
    network_device: [
        CONSTANT.DATA_TABLE.COLUMN.CHECKBOX,
        CONSTANT.DATA_TABLE.COLUMN.ID_LINK,
        {data: 'name', width: '100px'},
        {data: 'sn', width: '150px'},
        {data: 'networkdevice__device_type'},
        {data: 'networkdevice__port_num'},
        {data: 'manage_ip'},
        {data: 'idc__name'},
        {data: 'business_unit__name'},
        {data: 'admin__email'},
        CONSTANT.DATA_TABLE.COLUMN.OPERATION
    ],
    storage: [
        CONSTANT.DATA_TABLE.COLUMN.CHECKBOX,
        CONSTANT.DATA_TABLE.COLUMN.ID_LINK,
        {data: 'name', width: '100px'},
        {data: 'sn', width: '150px'},
        {data: 'storage__storage_type'},
        {data: 'storage__capacity'},
        {data: 'storage__interface_type'},
        {data: 'idc__name'},
        {data: 'business_unit__name'},
        {data: 'admin__email'},
        CONSTANT.DATA_TABLE.COLUMN.OPERATION
    ],
    virtual_machine: [
        CONSTANT.DATA_TABLE.COLUMN.CHECKBOX,
        {data: 'id', width: '30px'},
        {data: 'name', width: '100px'},
        {data: 'manage_ip'},
        {data: 'os_type'},
        {data: 'os_distribution'},
        {data: 'host__name'},
        {data: 'host__manage_ip'},
        CONSTANT.DATA_TABLE.COLUMN.OPERATION
    ],
    asset_approval: [
        CONSTANT.DATA_TABLE.COLUMN.CHECKBOX,
        {data: 'id', width: '30px'},
        {data: 'sn', width: '150px'},
        {data: 'asset_type', width: '80px'},
        {data: 'model', width: '80px'},
        {data: 'manufacturer', width: '80px'},
        {data: 'date', width: '150px'},
        {data: 'status', width: '80px'},
        {data: 'approved_by'},
        {data: 'approved_date', width: '150px'},
        CONSTANT.DATA_TABLE.COLUMN.OPERATION
    ]
};
