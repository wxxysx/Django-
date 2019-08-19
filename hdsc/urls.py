"""hdsc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include,re_path
from app01.bin import Account,AdminIndex
from django.conf.urls import url
from django.views.static import serve
from hdsc import settings
urlpatterns = [
    # django后台管理链接
    path('admin/', admin.site.urls),
    # 注册
    path(r'reg/', Account.Register.as_view()),
    # 登录
    path(r'login/', Account.Login.as_view()),
    # 退出
    path(r'logout/', Account.Logout.as_view()),
    # 商城首页
    path(r'index/', AdminIndex.Index.as_view()),
    # 添加商品
    path(r'addgoods/', AdminIndex.AddGoods.as_view()),
    # 激活账号
    path(r'account/', Account.enable_accout.as_view()),
    # 商品详情页
    path(r'goodsdetail/', AdminIndex.GoodsDetail.as_view()),
    # 购物车
    path(r'cart/', AdminIndex.Cart.as_view()),
    # 下单支付页面
    path(r'order/', AdminIndex.Order.as_view()),
    # 收货地址编辑页面
    path(r'usercentersite/', AdminIndex.UserCenterSite.as_view()),
    # 基本信息浏览页面
    path(r'usercenterinfo/', AdminIndex.UserCenterInfo.as_view()),
    # 所有订单查看页面
    path(r'usercenterorder/', AdminIndex.UserCenterOrder.as_view()),
    # 管理员首页
    path(r'super/', AdminIndex.Super.as_view()),
    # 管理员订单处理
    path(r'orderprocessing/', AdminIndex.OrderProcessing .as_view()),
    # 评论显示
    path(r'treecomment/', AdminIndex.TreeComment .as_view()),
    # 评论
    path(r'comment/', AdminIndex.Comment .as_view()),
    # 商品列表
    path(r'goodslist/', AdminIndex.GoodsList .as_view()),
    # 设置密码
    path(r'newpwd/', Account.newpwd .as_view()),
    # 忘记密码
    path(r'resetpwd/', Account.resetpwd .as_view()),
    # 删除订单
    path(r'delorder/', AdminIndex.delorder .as_view()),
    # 信息修改
    path(r'setinfo/', AdminIndex.SetInfo .as_view()),
    # 评论管理
    path(r'setcomment/', AdminIndex.SetComment .as_view()),
    # 管理员评论管理
    path(r'supersetcomment/', AdminIndex.SuperSetComment .as_view()),
    # 管理员 用户管理
    path(r'superuser/', AdminIndex.SetSuperUser .as_view()),
    # 管理员商品管理
    path(r'setsupergoods/', AdminIndex.SetSuperGoods.as_view()),
    # 管理员商品编辑
    path(r'goodsedit/', AdminIndex.GoodsEdit.as_view()),
    # 管理员登录页面
    path(r'adminlogin/', Account.SuperLogin.as_view()),
    # 管理员用户编辑
    path(r'useredit/', AdminIndex.UserEdit.as_view()),

# 配置meadia
    re_path(r'^media/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT}),
]
