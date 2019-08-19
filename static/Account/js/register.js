$('input[name="csrfmiddlewaretoken"]').val('****************')

// 错误信息的隐藏
$('.form-control').focusin(function () {
    $('#error_'+$(this)[0].id).fadeOut()
})
// 数据上传
$("#reg_sub").click(function () {


    var token=document.cookie.split('=')[1]

    var form_list=$('#form').serializeArray()

    var error=[]
    // #先创建一个FormData，用来存放Form表单数据
    var formdata=new FormData()
    for (var index in form_list){
        var name=form_list[index].name
        var val=form_list[index].value
        if (val==''){
            error.push('error_id_'+name)
        }else{
            if(name.search('csrf')==-1)
            formdata.append(name,val)
        }
    }


    if (error.length>0){

        for (var index in error){
            var error_obj=$('#'+error[index])
             error_obj.text('该字段不能为空！！')
             error_obj.fadeIn()
        }
    }
    else{

    $.ajax({
        url:"",
        headers:{'X-CSRFTOKEN':token},
        type:"post",
        contentType:false, //#数据预处理的编码格式
        processData:false,//#是否需要数据预处理，ajax上传文件不需要预处理，都交给FormData处理
        data:formdata,
        success:function (data) {
            var code=data['code']
            if (code==-1){
                var msg_list=data['msg']
                for (var k in msg_list){
                    //  有错误
                    if(k=='__all__'){
                        var error_obj=$('#error_id_r_pwd')
                    }else{
                    var error_obj=$('#error_id_'+k)}
                    error_obj.text(msg_list[k][0])
                    error_obj.fadeIn()
                }
            }else if(code==1){

            //    成功之后
                location.href='/login'

            }
        }
    })}
}
)