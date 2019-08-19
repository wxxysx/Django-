
var parent_comment=null

//评论
$("#btn_comment_submit").click(function () {
    $(".commentbox_title_left").html('评论内容：')

    var article_id = document.getElementById('div_digg').className
    var content = $("#tbCommentBody").val();
    var token = $('input[name="csrfmiddlewaretoken"]').val()

    $.ajax({
        url: '/comment/',
        type: 'post',
        dataType: 'json',
        // headers: {'X-CSRFTOKEN': token},
        data: {'article_id': article_id, 'content': content, 'parent_comment': parent_comment,'csrfmiddlewaretoken':token},
        success: function (data) {
            if(data['code']){

            var comment = `<ul class="list-group">
                    <li class="list-group-item">
                        <span class="comment_date">${data.date}</span><!--显示时间-->
                        <span id="a_comment_author_${data.nid}"  target="_blank">${data.user}</span><!--评论者-->
                        <a href="javascript:void(0);" id="${data.nid}" user="${data.user}" class="Reply">回复</a>
                    </li>
                    <li class="list-group-item">
                        <div id="comment_body_${data.nid}" class="blog_comment_body" style="font-size: 13px;margin-left: 10px "><b>${data.content}</b></div><!--显示评论内容-->
                   </li>
                </ul>`

            $("#comments_pager_bottom").html(comment)
            }else {

                $('.eror_msg').html(data['msg'])
            }

        }

    })
})



//显示树状结构评论
show_comment(0)
function show_comment (page){

    var token=$('input[name="csrfmiddlewaretoken"]').val()
    $.ajax({
        url: '/treecomment/',
        type: 'post',
        data: {'article_id': $("#article_id").attr("class"), 'csrfmiddlewaretoken': token,'page':page},
        dataType: 'json',
        // headers:{'X-CSRFTOKEN':token},
        success: function (data) {
            $(".feedbackNoItems").html('')
            var page = data.page
            data = data.data
            $(".temp_msg").fadeOut(3)
            $.each(data, function (index, item) {
                // 格式化时间
                var date = new Date(item[4]);
                Y = date.getFullYear() + '-';
                M = (date.getMonth() + 1 < 10 ? '0' + (date.getMonth() + 1) : date.getMonth() + 1) + '-';
                D = (date.getDate() < 10 ? '0' + date.getDate() : date.getDate()) + ' ';
                h = (date.getHours() < 10 ? '0' + date.getHours() : date.getHours()) + ':';
                m = (date.getMinutes() < 10 ? '0' + date.getMinutes() : date.getMinutes()) + ':';
                s = (date.getSeconds() < 10 ? '0' + date.getSeconds() : date.getSeconds());
                item[4] = Y + M + D + h + m + s
                //格式化时间结束
                var tree = {}
                //这里使用的功能类似于python的字符串格式化
                //树状评论实现的思路：
                //    1.每一条评论都有自己的ul
                //    2.子评论的数据中带有父评论的ID，然后找到父评论将子评论插入到父评论的ul中
                //    3.在css样式用加入样式使评论往右偏移10px，由于子评论在父评论中，会使子评论比父评论多往右偏移10px
                var comment = `
                <ul class="list-group" id="${item[0]}">
                    <li class="list-group-item">
                        <!--<a href="#" class="layer">#${index + 1}</a>&lt;!&ndash;显示楼层&ndash;&gt;-->
                        <span class="comment_date">${item[4]}</span><!--显示时间-->
                        <span id="a_comment_author_${item[0]}"  target="_blank">${item[2]}</span><!--评论者-->
                        <!--<a href="javascript:Reply($('#${item[0]}'));" id="${item[0]}" user="${item[2]}" class="Reply">回复</a>-->
                    </li>
                    <li class="list-group-item">
                        <div id="comment_body_${item[0]}" class="blog_comment_body" style="font-size: 13px;margin-left: 10px"><b>${item[3]}</b></div><!--显示评论内容-->
                   </li>
                    <li class="list-group-item" id="ChildComment"></li>
                </ul>
`
                if (!item[5]) {
                    $(".feedbackNoItems").append(comment)
                } else {
                    $("#" + item[5] + ">#ChildComment").append(comment)
                }
            })
            // $('.uppage')[0].id = Number(page-1)
            // $('.downpage')[0].id = Number(page+1)
        }
    })

}

$('.uppage').click(function () {
    show_comment(Number($(this)[0].id))
})
$('.downpage').click(function () {
    show_comment(Number($(this)[0].id))
})
//回复
function Reply (doc) {
    parent_comment=doc.attr('id')
    $(".commentbox_title_left").html('回复：'+doc.attr('user'))
    $("#tbCommentBody").focus()
}