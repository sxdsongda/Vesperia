/**
 * Created by Daniel on 2016/8/25.
 */

(function($){
    $.fn.serializeJson=function(){
        var serializeObj={};
        var array=this.serializeArray();
        var str=this.serialize();
        $(array).each(function(){
            if(serializeObj[this.name]){
                if($.isArray(serializeObj[this.name])){
                    serializeObj[this.name].push(this.value);
                }else{
                    serializeObj[this.name]=[serializeObj[this.name],this.value];
                }
            }else{
                serializeObj[this.name]=this.value;
            }
        });
        return serializeObj;
    };
    $.fn.loadJson=function (jsonObj) {
        var obj = jsonObj;
        var value, tagName, type;
        for (var key in obj){
            value = obj[key];
            $("[name="+key+"]", this).each(function () {
                tagName = $(this)[0].tagName;
                if(tagName=='INPUT'){
                    type = $(this).attr('type');
                    if(type=='radio'){
                        $(this).attr('checked',$(this).val()==value);
                    }else if(type=='checkbox'){
                        for(var i =0;i<value.length;i++){
                            if($(this).val()==value[i]){
                                $(this).attr('checked',true);
                                break;
                            }
                        }
                    }else{
                        $(this).val(value);
                    }
                }else if (tagName=='SELECT'){
                    // select2把select标签画成了别的的东西，常规的select对象被jquery藏了起来，所以修改值的时候使用dom对象的触发器才行。
                    if ($(this).hasClass('select2-hidden-accessible')){
                        $(this).val(value).trigger('change')
                    }else {
                        $(this).val(value)
                    }
                }else if (tagName=='TEXTAREA'){
                    $(this).val(value)
                }
            })
        }
    }
})(jQuery);


