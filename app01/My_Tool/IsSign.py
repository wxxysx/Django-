from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse

# 在用户get或者post请求时如果用户没有登录，则跳转到登录页面
class LoginRequired(object):
    @method_decorator(login_required(login_url='/login/'))
    def dispatch(self,request,*args,**kwargs):
        return super(LoginRequired,self).dispatch(request,*args,**kwargs)



# 判断ajax是否登录
def chack():
    def _wrapper(func):
        def __wrapper(self,request, *args, **kwargs):
                if request.user.is_authenticated:
                    return func(self,request,*args, **kwargs)
                else:
                    return JsonResponse({'code':None,'msg':'未登录'})
        return __wrapper
    return _wrapper

