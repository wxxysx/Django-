from django.conf import settings
from django.shortcuts import render,HttpResponse,redirect
from django.http import JsonResponse
from django.views import View
from app01 import models
from app01.My_Tool.IsSign import LoginRequired,chack
# 导入事件函数
from django.db import transaction
from django.contrib.auth.hashers import make_password
import time
from app01.form_model.verification.form_verification import AddGoodsForm,EditGoods,EditUser
import random
import json
from app01.plug.page.paging import page
from django.db.models import F

class Index(View):
    '''
    首页
    '''
    def get(self,request):
        '''
        浏览商品界面

        :param request:
        :return:
        '''

        # 获取商品类别，用户类别的显示
        goodsclass = models.GoodsClass.objects.all().values('pk','title','img','style')
        index_goods = []
        # 根据类别来获取商品，由于首页商品
        for item in goodsclass:
            t = models.Goods.objects.filter(goodsclass_id=item.get('pk')).values('pk','name','price','stock','goodsimg__img','goods_details','goodsclass')
            temp = t
            # 由于首页每个类别的商品数量显示为四个，所以如果商品数量少于等于4 则直接显示，否则随机挑选四个
            if len(t) > 4:
                tt = [i for i in t]
                temp = random.sample(tt,4)
            index_goods.extend(temp)
        # 如果当前用户已经登录，那么查询用户购物车数量
        if request.user.is_authenticated:
            shopping_car = models.ShoppingCart.objects.filter(user=request.user)
        else:
            shopping_car = []

        return render(request,'index/index.html',{'goodsclass':goodsclass,'index_goods':index_goods,'shopping_car_count':len(shopping_car)})

class AddGoods(View):
    '''
    添加商品
    '''
    def get(self,request):
        # 判断当前用户是否为管理员
        if not request.user.is_super:
            return HttpResponse('你不是管理员..')
        form = AddGoodsForm()

        return render(request, 'index/addgoods.html',{'form':form})

    def post(self,request):
        '''
        使用modelform来添加商品，
        :param request:
        :return:
        '''
        form = AddGoodsForm(request.POST)
        res = {'user': None, 'msg': None, 'code': 0}
        if not request.user.is_super:
            return JsonResponse( {'user': None, 'msg': '你不是管理员...', 'code': 0})
        if form.is_valid():

            goods = form.cleaned_data
            file_obj1 = request.FILES.get('img')
            t1 = time.time()
            extra_fields1 = {}
             # 为了避免文件命重复的清空，使用时间戳来命名文件
            file_obj1.name = '%s_%s_%s' % (t1, request.user.username, file_obj1.name)
            extra_fields1['img'] = file_obj1

            goodsclass = models.GoodsClass.objects.filter(pk=goods.get('goodsclass')).first()
            if goodsclass:
                # 使用数据库事件，如果以下数据库操作有一条执行失败，那么所有的操作都不生效
                with transaction.atomic():
                    # 插入商品
                    goods = models.Goods.objects.create(
                        name=goods.get('name'),
                        price=goods.get('price'),
                        stock=goods.get('stock'),
                        goodsclass = goodsclass,
                        goods_details=goods.get('goods_details'),
                        user=request.user,

                    )
                    # 插入商品图片
                    models.GoodsImg.objects.create(goods=goods,**extra_fields1)
                    res['user'] = form.cleaned_data.get('user_name')
                    res['code'] = 1
            else:
                res['user'] = '商品类型错误'
                res['code'] = -1
        else:
            res['msg'] = form.errors
            res['code'] = -1
        return JsonResponse(res)
class GoodsList(View):
    '''
    商品列表页面
    '''
    def get(self,request):
        price_flag = None
        f = ''
        param = self.request.GET.copy()
        # 默认按钮
        d = self.request.GET.copy()
        d['order'] = ''
        d = d.urlencode()
        data = request.GET
        # 获取用户要查看的商品列别
        c = data.get('class')
        # 获取用户搜索的商品名称
        search = data.get('goods_name')
        # 获取用户要的排列方式
        order = data.get('order')
        if c:# 判断用户是否提交商品类别  如果提交了 则按照类别来显示
            goods_list = models.Goods.objects.filter(goodsclass_id=c).values('pk','name','price','stock','goodsimg__img','goods_details','goodsclass','goodsclass__title')
        if search:# 判断用户是否提交商品名称  如果提交了 则按照名称来显示
            goods_list = models.Goods.objects.filter(name__contains=search).values('pk', 'name', 'price', 'stock',
                                                                             'goodsimg__img', 'goods_details',
                                                                             'goodsclass',
                                                                             'goodsclass__title')
        if not c and not search: # 如果没有类别 也没有名称，那么默认显示全部商品
            goods_list = models.Goods.objects.all().values('pk', 'name', 'price', 'stock',
                                                                                   'goodsimg__img', 'goods_details',
                                                                                   'goodsclass',
                                                                                   'goodsclass__title')
        if order == '1' or order == 1: # 排序方式，如果为1 价格升序 如果为0 价格降序
            price_flag = 'active'
            f = '^'
            param['order'] = 0
            goods_list = goods_list.order_by('price')
            order = '0'
        elif order == '0' or order == 0:
            f='ˇ'
            param['order'] = 1
            price_flag = 'active'
            goods_list = goods_list.order_by('-price')
            order = '1'
        # 获取所有商品，用来随机显示新品推荐

        goods_all = models.Goods.objects.all().values('pk', 'name', 'goodsimg__img', 'goods_details',
                                                      'goodsclass__title', 'price')
        if c:# 再次判断用户是否有提交类别，如果有按照类别来随机显示新品推荐
            goods_all = goods_all.filter(goodsclass_id=c)
        # 获取商品类别，用户页面显示
        goodsclass = models.GoodsClass.objects.all()
        shopping_car = []
        # 如果用户登录了，那么获取购书车信息
        if request.user.is_authenticated:
            shopping_car = models.ShoppingCart.objects.filter(user=request.user)
        # 获取分页信息

        now_num = param.get('page')
        page_view = page(goods_list.count(), request.path, url_params=param, now_page=now_num, each_count=15)
        goods_list = goods_list[page_view.start():page_view.end()]
        goods_c = goods_all
        # 显示新品推荐
        if len(goods_all)>2:
            goods_c = [i for i in goods_all]
            goods_c = random.sample(goods_c,2)
        url_p = param.urlencode()
        return render(request,'index/list.html',{'d': d,'f':f,'price_flag':price_flag,'goods_list':goods_list,'goodsclass':goodsclass,'shopping_car_count':len(shopping_car),'page':page_view.page_option(),'goods_c':goods_c,'order':order,'p':url_p})

class GoodsDetail(View):
    def get(self,request):
        # 获取用户上传的，商品ID
        gid = request.GET.get('goodsid')
        # 按照id获取商品
        goods = models.Goods.objects.filter(pk=gid).values('pk','name','goodsimg__img','goods_details','goodsclass__title','price','goodsclass_id','goodsclass_id').first()
        # 根据商品类别，获取商品，用户新品推荐
        goods_all = models.Goods.objects.all().values('pk','name','goodsimg__img','goods_details','goodsclass__title','price').filter(goodsclass_id=goods.get('goodsclass_id'))
        #  以下代码 跟上面一样，不做注释
        goodsclass = models.GoodsClass.objects.all()
        goods_c = goods_all

        if len(goods_all) > 2:
            goods_c = [i for i in goods_all]
            goods_c = random.sample(goods_c,2)
        shopping_car = []
        # 判断用户是否登录，如果登录，存入浏览历史
        if request.user.is_authenticated:
            shopping_car = models.ShoppingCart.objects.filter(user=request.user)
            flag = models.Browsing.objects.filter(user=request.user,goods_id=gid)
            # 判断当前商品的浏览历史是否存在，如果不存在则新建，如果存在更新浏览时间为当前时间
            if not flag:
                models.Browsing.objects.create(user=request.user,goods_id=gid,Time=time.time())
            else:
                import datetime
                flag.update(Time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


        return render(request,'index/detail.html',{'goods':goods,'goodsclass':goodsclass,'goods_c':goods_c,'shopping_car_count':len(shopping_car)})
    @chack()
    def post(self,request):
        '''
        加入购物车，或者立即购买
        :param request:
        :return:
        '''
        res = {'code':None,'msg':None,'shopping_car_count':None}
        # 获取商品id
        goodsid = request.POST.get('goodsid')
        # 获取商品数量
        count = request.POST.get('count')
        # 获取标志 用于判断是立即购买 还是加入购物车
        flag = request.POST.get('flag')
        # 判断是否为加入购物车
        if not flag:
            # 加入购物车，判断购物车用是否有同样的商品
            f = models.ShoppingCart.objects.filter(user=request.user,goods_id=goodsid)
            if not f:
                # 没有：新建
                models.ShoppingCart.objects.create(user=request.user,goods_id=goodsid,count=count)
            else:
                # 有添加数量
                f.update(count=F('count')+count)
            shopping_car = models.ShoppingCart.objects.filter(user=request.user)
            res['code'] = 1
            res['msg'] = '加入购物车成功..'
            res['shopping_car_count'] = len(shopping_car)
        else:
            # 如果是立即购买，那么新建订单
            goods = models.Goods.objects.filter(pk=goodsid).values('user_id').first()
            models.Order.objects.create(seller_id=goods.get('user_id'),customer=request.user,goods_id=goodsid,count=count)
            res['code'] = 1
        return JsonResponse(res)

class Cart(LoginRequired,View):
    def get(self,request):
        # 购物车显示
        cart_list = models.ShoppingCart.objects.filter(user=request.user).values('pk','count','goods__name','goods__price','goods__goodsimg__img')

        return render(request,'index/cart.html',{'cart_list':cart_list,'shopping_car_count':len(cart_list)})

    def post(self,request):
        '''
        购买商品
            1.将选中的商品，添加到订单
            2.删除购物车中的记录
        :param request:
        :return:
        '''
        res = {'code':None,'msg':None}
        data = request.POST.get('goods_list')
        data =['%s}'%i  for i in data.split('},')]
        # 格式化上传的数据
        for item in data:
            item = item.replace('}}','}')
            item = json.loads(item)
            with transaction.atomic():
                # 查询购物车用的记录
                cart = models.ShoppingCart.objects.filter(pk=item.get('pdi'),user=request.user)
                # 将购物车中的记录更新到最新状态
                cart.update(count=item.get('count'))
                order = cart.values('goods__user','user','goods','count').first()
                cart.update(count=item.get('count'))
                # 将记录新建到，订单表中
                models.Order.objects.create(seller_id=order.get('goods__user'),customer=request.user,goods_id=order.get('goods'),count=order.get('count'),)
                # 删除购物车记录
                cart.delete()

        res['code'] = 1

        return JsonResponse(res)


class Order(LoginRequired,View):
    # 订单列表的显示
    def get(self,request):
        # 查询当前用户，所有未支付的订单
        order_list = models.Order.objects.filter(customer=request.user,pay__isnull=True).values('customer__address','goods__goodsimg__img','goods__price','count','goods__name')
        # 查询用户信息，用于显示收货人
        userinfo = models.UserInfo.objects.filter(pk=request.user.pk).values('name', 'phone', 'address','end_address').first()
        cart_list = models.ShoppingCart.objects.filter(user=request.user)
        address, name, phone = ['无','无','无']
        if userinfo.get('end_address'):
            address,name,phone = userinfo.get('end_address').split('||')

            # 将手机号加密处理
            if phone:
                phone = phone.replace(phone[3: -4], '****')

        return render(request,'index/place_order.html',{'order_list':order_list,'userinfo':userinfo,'phone':phone,'address':address,'name':name,'shopping_car_count':len(cart_list)})

    def post(self, request):
        res = {'code': None, 'msg': None}
        userinfo = models.UserInfo.objects.filter(pk=request.user.pk).values('name', 'phone', 'address',
                                                                             'end_address').first()
        if userinfo.get('end_address'):
            address, name, phone = userinfo.get('end_address').split('||')
            # 获取支付方式
            pay = request.POST.get('pay_style')
            # 格式化显示类容
            address ='%s (%s 收) %s'%( address,name,phone)
            # 1为货到付款，设置为未支付
            if str(pay) =='1':
                models.Order.objects.filter(customer=request.user, pay__isnull=True).update(pay=pay,end_address=address)
            # 其他为在线付款，设置为已付款
            else:
                models.Order.objects.filter(customer=request.user, pay__isnull=True).update(pay=pay,is_pay=True,end_address=address)
            res['code'] =1
        else:
            res['msg']='请先设置收货地址...'
        return JsonResponse(res)

class UserCenterSite(LoginRequired,View):
    '''
    用户信息修改
    '''
    def get(self,request):
        # 获取当前用户购物车信息 用于显示
        cart_list = models.ShoppingCart.objects.filter(user=request.user)
        # 获取用户信息
        userinfo = models.UserInfo.objects.filter(pk=request.user.pk).values('name','username','phone','end_address').first()
        end_address = userinfo.get('end_address')
        address, username, phone = ['无','无','无']
        if end_address:
            address,username,phone = end_address.split('||')
            phone = phone.replace(phone[3: -4],'****')
        return render(request,'index/user_center_site.html',{'userinfo':userinfo,'phone':phone,'shopping_car_count':len(cart_list),'address':address,'username':  username})



    def post(self,request):
        res = {'code': None, 'msg': None}
        data = request.POST
        print(data)
        end_address = '%s||%s||%s'%(data.get('address'),data.get('name'),data.get('phone'))
        # 根据上传的数据，更新用户信息 name=data.get('name') 惠州惠东 （ 收） 134****29377
        models.UserInfo.objects.filter(username=request.user.username).update(end_address=end_address)
        res['code'] = 1
        return JsonResponse(res)

class UserCenterInfo(LoginRequired,View):
    '''
    查看用户信息，跟上面一样，不做注释
    '''
    def get(self,request):
        cart_list = models.ShoppingCart.objects.filter(user=request.user)
        goods = models.Browsing.objects.filter(user=request.user).order_by('-Time')[0:3].values('goods__name','goods__price','goods__goodsimg__img','goods_id')

        return render(request,'index/user_center_info.html',{'shopping_car_count':len(cart_list),'goods':goods})


class UserCenterOrder(LoginRequired,View):

    def get(self,request):
        # 查看订单信息
        orders = models.Order.objects.filter(customer=request.user).order_by('is_pay')
        # 获取分页信息
        param = self.request.GET.copy()
        now_num = param.get('page')
        page_view = page(orders.count(), request.path, url_params=param, now_page=now_num, each_count=2)
        cart_list = models.ShoppingCart.objects.filter(user=request.user)
        orders_list = orders[page_view.start():page_view.end()].values('order_time','pk','is_pay','count','goods__goodsimg__img','goods__price','goods__name','pay','is_deliver','is_collect')
        return render(request,'index/user_center_order.html',{'orders_list':orders_list,'shopping_car_count':len(cart_list),'page':page_view.page_option()})

    def post(self,request):
        # 收货
        res = {'code':None,'msg':None}
        order_id = request.POST.get('order_id')
        # 更新状态，已收货，已付款
        models.Order.objects.filter(customer=request.user,pk=order_id).update(is_collect=True,is_pay=True)

        res['code'] = 1

        return JsonResponse(res)
class Super(LoginRequired,View):
    # 管理员页面
    def get(self,request):
        if not request.user.is_super:
            return HttpResponse('你不是管理员...')

        return render(request,'index/adminindex.html')

class OrderProcessing(LoginRequired,View):
    # 订单处理
    def get(self,request):
        if not request.user.is_super:
            return HttpResponse('你不是管理员...')
        # 查询订单信息，并分页
        order_list = models.Order.objects.filter(seller=request.user)
        param = self.request.GET.copy()
        now_num = param.get('page')
        page_view = page(order_list.count(), request.path, url_params=param, now_page=now_num, each_count=5)
        order_list = order_list.order_by('is_deliver','is_pay')[page_view.start():page_view.end()].values(
            'customer__username','goods__name','goods__goodsimg__img','goods__price','count','is_pay',
            'pay','is_deliver','end_address','pk','order_time','goods__price','is_collect'
        )
        pay_choices = models.Order.pay_choices
        for item in order_list:
            if item.get('pay'):
                item['pay'] = pay_choices[item['pay']-1][1]
            else:
                item['pay'] = '未付款'

        return render(request,'index/super_order_list.html',{'order_list':order_list,'pay_choices':models.Order.pay_choices,'page':page_view.page_option()})


    def post(self,request):
        '''
        发货
        :param request:
        :return:
        '''
        res = {'code': None, 'msg': None}
        if not request.user.is_super:
            res['msg'] = '你不是管理员...'
            return JsonResponse(res)

        order_id = request.POST.get('order_id')
        # 更新信息为已发货
        models.Order.objects.filter(pk=order_id,seller=request.user).update(is_deliver=True)
        res['code'] = 1
        return JsonResponse(res)


class TreeComment(View):
    '''
    评论显示
    '''
    def post(self,request):
        res = {'code':None,'msg':None}
        article_id = request.POST.get('article_id')
        obj =  models.Comment.objects.filter(goods_id=article_id).order_by('pk')

        # 获取分页信息
        param = self.request.POST.copy()
        now_num = param.get('page')
        page_view = page(obj.count(), request.path, now_page=now_num, each_count=3)

        orders_list =list( obj[page_view.start():page_view.end()].values_list('pk', 'goods',
                                                                                          'user__username',
                                                                                          'text', 'create_time',
                                                                                          'parent_comment'))
        if int(now_num) * 3 > obj.count():
            now_page = obj.count() // 3

        else:
            now_page = page_view.now_page

        return JsonResponse({'data': orders_list,'page':now_page})




# 评论
class Comment(View):
    '''
    提交评论
    '''
    def post(self,request):
        flag1 = models.Comment.objects.filter(user=request.user) # 判断是否已经评论过
        flag2 = models.Order.objects.filter(customer=request.user,is_collect=True) # 判断是否购买过商品
        res = {'code':None,'msg':'您已经评论过,或者未购买此商品'}
        if not flag1 and flag2: # 两个条件都通过，才可以评论
            data=request.POST
            user=request.user
            content=data.get('content')
            if data.get('parent_comment'):
                parent_comment=models.Comment.objects.filter(nid=data.get('parent_comment')).first()

            else:
                parent_comment=None
            CommentObj=models.Comment.objects.create(goods_id=data.get('article_id'),text=content,parent_comment=parent_comment,user=user)
            if parent_comment:
                parent_comment=CommentObj.parent_comment.nid

            res={'code':1,'nid':CommentObj.pk,'user':request.user.username,'content':CommentObj.text,'ArticleId':CommentObj.goods_id,'ParentComment':parent_comment,'date':CommentObj.create_time.strftime("%Y-%m-%d %H:%M:%S")}

        return JsonResponse(res)


class delorder(LoginRequired,View):
    '''
    删除订单 根据上传不的订单号，删除
    '''
    def post(self,request):
        res = {'code':None,'msg':None}
        order_id  = request.POST.get('goods_id')
        models.ShoppingCart.objects.filter(user=request.user,pk=order_id).delete()
        res['code'] = 1

        return JsonResponse(res)


class SetInfo(LoginRequired,View):
    # 设置信息
    def get(self,request):
        cart_list = models.ShoppingCart.objects.filter(user=request.user)

        return render(request,'index/user_center_pwd.html',{'shopping_car_count':len(cart_list)})

    def post(self,request):
        res = {'code':None,'msg':None}
        data = request.POST
        name = data.get('name')
        phone = data.get('phone')
        address = data.get('address')
        password = data.get('pwd')
       # 根据上传的信息，更新 name=name,
        if password !='':
            models.UserInfo.objects.filter(pk=request.user.pk).update(phone=phone,address=address,password=make_password(password))
        else:
            models.UserInfo.objects.filter(pk=request.user.pk).update(phone=phone,address=address,)
        res['code'] =1
        return JsonResponse(res)


class SetComment(LoginRequired,View):
    '''
    评论处理
    '''
    def get(self,request):
        comm_list = models.Comment.objects.filter(user=request.user)

        # 获取分页信息
        param = self.request.GET.copy()
        now_num = param.get('page')
        page_view = page(comm_list.count(), request.path, url_params=param, now_page=now_num, each_count=5)
        cart_list = models.ShoppingCart.objects.filter(user=request.user)
        comm_list = comm_list[page_view.start():page_view.end()].values('goods__name','pk','text','create_time')

        return render(request,'index/user_center_comm.html',{'comm_list':comm_list,'shopping_car_count':len(cart_list),'page':page_view.page_option()})

    def post(self,request):
        '''
        根据上传的评论ID 删除评论,普通用户只能删除自己的评论
        :param request:
        :return:
        '''
        res = {'code': None, 'msg': None}
        data = request.POST
        models.Comment.objects.filter(user=request.user,pk=data.get('id')).delete()
        res['code'] = 1

        return JsonResponse(res)


class SuperSetComment(LoginRequired,View):
    '''
    管理员用户删除评论
    '''
    def get(self,request):
        # 显示评论列表
        comm_list = models.Comment.objects.all()
        param = self.request.GET.copy()
        now_num = param.get('page')
        page_view = page(comm_list.count(), request.path, url_params=param, now_page=now_num, each_count=5)
        comm_list = comm_list[page_view.start():page_view.end()].values('goods__name','pk','text','create_time','user__username')
        return render(request,'index/super_comment_list.html',{'comm_list':comm_list,'page':page_view.page_option()})

    def post(self,request):
        # 根据上传的ID 删除评论，无需判断评论人
        res = {'code': None, 'msg': None}
        data = request.POST
        if request.user.is_super:
            models.Comment.objects.filter(pk=data.get('order_id')).delete()
            res['code'] =1
        return JsonResponse(res)

class SetSuperUser(LoginRequired,View):
    '''
    设置用户
    '''
    def get(self,request):
        '''
        显示用户
        :param request:
        :return:
        '''
        userlist = models.UserInfo.objects.filter(is_super=False).all()
        param = self.request.GET.copy()
        now_num = param.get('page')
        page_view = page(userlist.count(), request.path, url_params=param, now_page=now_num, each_count=5)
        userlist = userlist[page_view.start():page_view.end()].values('pk','username','address','email','phone')
        return render(request,'index/super_user_list.html',{'userlist':userlist,'page':page_view.page_option()})

    def post(self,request):
        '''
        删除用户
        :param request:
        :return:
        '''
        res = {'code': None, 'msg': None}
        data = request.POST
        if request.user.is_super:
            models.UserInfo.objects.filter(pk=data.get('order_id')).delete()
            res['code'] = 1
        return JsonResponse(res)


class SetSuperGoods(LoginRequired,View):
    '''
    设置商品
    '''
    def get(self,request):
        # 浏览商品
        goods_list = models.Goods.objects.all()
        param = self.request.GET.copy()
        now_num = param.get('page')
        page_view = page(goods_list.count(), request.path, url_params=param, now_page=now_num, each_count=5)
        goods_list = goods_list[page_view.start():page_view.end()].values('pk','name','price')
        return render(request,'index/super_goods_list.html',{'goodslist':goods_list,'page':page_view.page_option()})

    def post(self,request):
        #删除商品
        res = {'code': None, 'msg': None}
        data = request.POST

        if request.user.is_super:
            models.Goods.objects.filter(pk=data.get('order_id')).delete()
            res['code'] = 1
        return JsonResponse(res)

class GoodsEdit(LoginRequired,View):
    '''
    修改商品信息
    '''
    def get(self,request):

        gid = request.GET.get('gid')
        goods = models.Goods.objects.filter(pk=gid).first()
        form = EditGoods(instance=goods)
        img = models.GoodsImg.objects.filter(goods=goods).values('img').first()

        return render(request, 'index/editgoods.html', {'form': form, 'goods': goods,'img':img})

    def post(self,request):
        res = {'code':None,'msg':None}
        gid = request.POST.get('gid')
        new_goods = EditGoods(request.POST)

        if new_goods.is_valid():
            file_obj1 = request.FILES.get('img')
            # 验证通过，使用save()方法保存数据
            t1 = time.time()
            extra_fields1 = {}

            if file_obj1:
                file_obj1.name = '%s_%s_%s' % (t1, request.user.username, file_obj1.name)
                extra_fields1['img'] = file_obj1


                models.GoodsImg.objects.filter(goods_id=gid).delete()

                goodsimg = models.GoodsImg.objects.create(goods_id=gid,**extra_fields1)

            models.Goods.objects.filter(pk=gid).update(**new_goods.cleaned_data)

            res['code'] = 1
            return JsonResponse(res)


class UserEdit(LoginRequired,View):
    '''
    修改用户信息
    '''
    def get(self,request):
        uid = request.GET.get('uid')
        user = models.UserInfo.objects.filter(pk=uid).first()
        form = EditUser(instance=user)
        return render(request,'index/edituser.html',{'form':form})

    def post(self,request):
        form = EditUser(request.POST)
        uid = request.GET.get('uid')

        if form.is_valid():
            models.UserInfo.objects.filter(pk=uid).update(**form.cleaned_data)

        return redirect('/superuser')