from django.conf import settings
from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.views import View
from app01 import models
from django.contrib import auth
from django.core.mail import send_mail # 发送邮件模块
import threading
import time
from django.contrib.auth.hashers import make_password

class Register(View):
    '''
    注册事件
    post ：
        1.查询数据库中是否已经有当前用户名 如果没有
        2.使用time模块生成时间戳，用于激活账号
        3.创建一个线程，发送激活邮件
        4.在邮件发送过程中，如果出错，则删除用户记录。注册失败
    '''
    def get(self,request):

        return render(request, 'Account/register.html')

    def post(self,request):

        res = {'user': None, 'msg': None, 'code': None}
        data = request.POST
        username = data.get('username')
        pwd = data.get('pwd')

        email = data.get('email')
        if models.UserInfo.objects.filter(username=username):
            res['msg'] = '账号已被注册...'
        else:
            temp_user = models.UserInfo.objects.create_user(username=username,password=pwd,email=email,key=time.time())
            t = threading.Thread(target=self.send_email_my,args=(temp_user,))
            t.start()
            res['code'] = 1
        return JsonResponse(res)

    def send_email_my(self, temp_user):
        try:
            text = '感谢您成为惠东水产销售网站的用户，请点击网址激活账号，http://127.0.0.1:8000/account/?key=%s' % temp_user.key
            send_mail('激活', text, settings.EMAIL_HOST_USER, [temp_user.email, ]
                      )

        except Exception as e:
            print(e)
            temp_user.delete()

# 激活账号
class enable_accout(View):
    '''
    激活账号
        如果用户访问了激活链接，将账号设置为可用
    '''
    def get(self,request):

        temp =models.UserInfo.objects.filter(key=request.GET.get('key'))
        if temp:
            temp.update(is_enabled=True)
        return redirect('/login')


# 忘记密码
class newpwd(View):
    '''
    忘记密码
        1.填写注册时使用的邮箱和用户名
        2.判断邮箱用户名是否匹配
        3.更新时间戳，用户密码更改
        4.创建一个线程，发送邮件

    '''

    def get(self,request):
        return render(request,'Account/newpwd.html')

    def post(self,request):
        res = {'code': None, 'msg': None}
        data = request.POST
        auth.get_user_model()
        account = data.get('username')
        email = data.get('pwd')
        temp_user = models.UserInfo.objects.filter(username=account, email=email)
        if temp_user:
            res['code']=1
            temp_user.update(key=time.time())
            t = threading.Thread(target=self.send_email_my,args=(temp_user.first(),))
            t.start()
        else:

            res['msg'] = '账号邮箱不匹配'
        return JsonResponse(res)


    def send_email_my(self, temp_user):
        text = '你好，请点击网址修改密码，http://127.0.0.1:8000/resetpwd/?key=%s' % temp_user.key
        send_mail('修改密码', text, settings.EMAIL_HOST_USER, [temp_user.email, ]
                      )

class resetpwd(View):
    def get(self,request):
        return render(request,'Account/resetpwd.html')
    def post(self,request):
        key = request.GET.get('key')
        res = {'code': None, 'msg': None}
        tempuser = models.UserInfo.objects.filter(key=key)
        if tempuser:
            pwd = request.POST.get('username')
            tempuser.update(password=make_password(pwd))
            tempuser.update(key=time.time())
            res['code']=1
        else:
            res['msg'] = '用户不存在'
        return JsonResponse(res)
class Login(View):
    '''
    登录，判断用户密码 和 账号是否激活
    '''
    def post(self,request):
        response_data = {'mag': None, 'code': None}
        #取出用户输入的用户名
        user=request.POST.get('username')
        #去出用户输入的密码
        pwd=request.POST.get('pwd')
        next = request.GET.get('next')
        response_data['next'] = next
        user = auth.authenticate(username=user, password=pwd)
        if user:
            if user.is_enabled:
                auth.login(request,user)
                response_data['mag']='%s,登录成功....'%user
                if user.is_super:
                    response_data['code'] = 2
                else:
                    response_data['code']=1
            else:
                response_data['mag'] = '用户未激活，请到所填的邮箱中激活'
                response_data['code'] = None
        else:
            response_data['mag']='用户名或密码错误...'


        return JsonResponse(response_data)

    def get(self,request):

        return render(request, 'Account/login.html')

    # 注销

class SuperLogin(View):
    '''
    管理员登录
    '''
    def post(self,request):
        response_data = {'mag': None, 'code': None}
        #取出用户输入的用户名
        user=request.POST.get('username')
        #去出用户输入的密码
        pwd=request.POST.get('pwd')

        # user=auth.authenticate(username=user,password=pwd)


        user = auth.authenticate(username=user, password=pwd)
        if user:
            if user.is_enabled:
                auth.login(request,user)
                response_data['mag']='%s,登录成功....'%user
                response_data['code']=2
            else:

                response_data['mag'] = '用户未激活'
                response_data['code'] = None
        else:
            response_data['mag']='用户名或密码错误...'


        return JsonResponse(response_data)

    def get(self,request):

        return render(request, 'Account/adminlogin.html')

    # 注销
class Logout(View):
    '''
    退出
    '''
    def get(self, request):
        if request.user.is_super:
            auth.logout(request)
            return redirect('/adminlogin/')
        auth.logout(request)
        return redirect('/index/')