from django import template

#变量名称不能变 Django固定名称
register=template.Library()


def get_is_super(request):
    is_super = False
    is_login = False
    if request.user.is_authenticated:  # 判断当前用户是否登录，如果登录，在判断是否管理员用户
        is_login = True
        is_super = request.user.roles.filter(title='SUPERUSER')

    return {'is_login':is_login,'is_super':is_super}



#使用此方法可以实现的功能是
# get_tag_data(user,blog)获取此函数的返回值，然后将返回值返回到@register.inclusion_tag('inclution/LeftDive.html')指定的
#模板然后进行渲染
@register.inclusion_tag('include/left_menu.html')
def is_super(request):
    return get_is_super(request)

# @register.inclusion_tag('inclution/TagAndCategory.html')
# # def GetTagCategory(user,blog):
# #     return get_tag(user,blog)