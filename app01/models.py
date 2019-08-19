from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    '''
    用户表
    '''
    email = models.CharField(verbose_name='邮箱', max_length=32)
    name = models.CharField(verbose_name='用户名',max_length=20)
    is_super = models.BooleanField(verbose_name='是否为管理员',default=False)
    phone = models.CharField(verbose_name='手机号',max_length=11,null=True)
    is_enabled = models.BooleanField(verbose_name='是否激活',default=False)
    key = models.CharField(verbose_name='激活码',max_length=256)
    address = models.CharField(verbose_name='联系地址',max_length=256,null=True)
    end_address = models.CharField(verbose_name='收货地址',max_length=256,null=True)
    gender_choices=(
        (1,'男'),
        (2,'女'),
    )
    gender = models.IntegerField(verbose_name='性别',default=1,choices=gender_choices)
    def __str__(self):
        return self.username


class Goods(models.Model):
    '''
    商品表
    '''
    name = models.CharField(verbose_name='商品名称',max_length=64)
    price = models.FloatField(verbose_name='价格')
    stock = models.IntegerField(verbose_name='库存')
    shelf_time = models.DateTimeField(verbose_name='上架时间',auto_now_add=True)
    user = models.ForeignKey(verbose_name='所属用户',to='UserInfo',on_delete=models.CASCADE)
    goodsclass = models.ForeignKey(verbose_name='类别',to='GoodsClass',on_delete=models.CASCADE )
    goods_details = models.CharField(verbose_name='商品详情',max_length=256)
    img_gg = models.FileField(verbose_name='广告图片', upload_to='good_img/', default='good_img/default.png')
    def __str__(self):
        return self.name
class GoodsImg(models.Model):
    '''
    商品图片表
    '''
    goods = models.ForeignKey(verbose_name='商品ID',to='Goods',on_delete=models.CASCADE)
    img = models.FileField(verbose_name='商品图片',upload_to='good_img/',default='good_img/default.png')


class GoodsClass(models.Model):
    '''
    商品类别表
    '''
    title = models.CharField(verbose_name='商品类别',max_length=16)
    img = models.FileField(verbose_name='类别图片',upload_to='good_img/',default='good_img/default.png')
    style = models.CharField(verbose_name='小图标',max_length=16,default='')

    def __str__(self):
        return self.title
class Order(models.Model):
    '''
    订单表
    '''

    seller = models.ForeignKey(verbose_name='商家',to='UserInfo',on_delete=models.CASCADE,related_name='user_seller')
    customer = models.ForeignKey(verbose_name='客户',to='UserInfo',on_delete=models.CASCADE,related_name='user_customer')
    goods = models.ForeignKey(verbose_name='商品',to='Goods',on_delete=models.CASCADE)
    count = models.IntegerField(verbose_name='商品数量')
    is_pay = models.BooleanField(verbose_name='是否已经付款',default=False)
    pay_choices = (
        (1, '货到付款'),
        (2, '支付宝'),
        (3, '微信'),
        (4, '银行卡'),
    )
    pay = models.IntegerField(verbose_name='付款方式', choices=pay_choices,null=True)
    is_deliver = models.BooleanField(verbose_name='是否发货',default=False)
    to_address = models.CharField(verbose_name='发货地址',max_length=256,default='')
    end_address = models.CharField(verbose_name='收货地址',max_length=256,default='')
    order_time = models.DateTimeField(verbose_name='下单时间',auto_now_add=True)
    pay_time = models.DateTimeField(verbose_name='付款时间',null=True)
    deliver_time = models.DateTimeField(verbose_name='发货时间',null=True)
    is_collect = models.BooleanField(verbose_name='是否收货',default=False)

class Browsing(models.Model):
    '''
    近期浏览表
    '''
    user = models.ForeignKey(verbose_name='用户',to='UserInfo',on_delete=models.CASCADE)
    goods = models.ForeignKey(verbose_name='商品',to='Goods',on_delete=models.CASCADE)
    Time = models.DateTimeField(verbose_name='浏览时间',null=True,auto_now_add=True)

class Comment(models.Model):
    '''
    评论表
    '''
    user = models.ForeignKey(verbose_name='评论人',to='UserInfo',on_delete=models.CASCADE)
    text = models.CharField(verbose_name='评论内容',max_length=256)
    goods = models.ForeignKey(verbose_name='评论的商品',to='Goods',on_delete=models.CASCADE)
    create_time = models.DateTimeField(verbose_name='评论时间', auto_now_add=True)
    parent_comment = models.ForeignKey('self',verbose_name='父级评论', null=True, on_delete=models.CASCADE)

class ShoppingCart(models.Model):
    '''
    购物车
    '''
    goods = models.ForeignKey(verbose_name='商品',to='Goods',on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name='用户',to='UserInfo',on_delete=models.CASCADE)
    count = models.IntegerField(verbose_name='数量')