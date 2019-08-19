$('input[name="csrfmiddlewaretoken"]').val('****************')


$('#form_input input').focus(function () {
    $('#error_mag').fadeOut()
})


$('#sub').click(function () {
    var form_dict={'user_name':$('#user_name').val(),'pwd':$('#pwd').val(),'verification_code':$('#verification_code').val()}
    var error=[]
    for (var k in form_dict){
        if (form_dict[k]==''){
            error.push(k)
        }
    }

    var token=document.cookie.split('=')[1]

    if (error.length>0){

    $('#error_mag').text(error.length+'个字段为空！！')
    $('#error_mag').fadeIn()

}else{
    $.ajax({
        url:'',
        type:'post',
        headers:{'X-CSRFTOKEN':token},
        data:{'user_name':$('#user_name').val(),'pwd':$('#pwd').val(),'verification_code':$('#verification_code').val()},
        success(data){
            var code=data['code']
            if (code==-1) {

                 $('#error_mag').text(data['mag'])
                 $('#error_mag').fadeIn()
             }else if(code==1){
                //  正确之后
                location.href='/index'
             }
        }
    })}
})


$('#register').click(function () {
    location.href='/reg'

})