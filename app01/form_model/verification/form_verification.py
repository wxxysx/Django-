from django.forms import widgets
from django import forms

from app01 import models

#使用钩子必须导入这个ValidationError错误，如果字段校验失败必须抛出这个错误
from django.core.exceptions import ValidationError
wid_text=widgets.TextInput(attrs={"class":"form-control"})
wid_cho=widgets.Select(attrs={"class":"form-control"}

                       )
wid_pwd=widgets.PasswordInput(attrs={"class":"form-control"})
wid_email=widgets.EmailInput(attrs={"class":"form-control"})

error_messages={'required':'该字段不能为空.....','max_length':'输入内容过长','min_length':'输入内容过短','invalid':'输入类型不合法....'}


class register(forms.Form):

    user_name=forms.CharField(min_length=5,
                              label='用户名',
                              widget=wid_text,
                              error_messages=error_messages,
                         )
    pwd=forms.CharField(min_length=8,
                        label='密码',
                        widget=wid_pwd,
                        error_messages=error_messages,)

    r_pwd=forms.CharField(min_length=8,
                          label='确认密码',
                          widget=wid_pwd,
                          error_messages=error_messages,)

    email = forms.EmailField(min_length=3,
                             label='邮箱',
                             widget=wid_text,
                             error_messages=error_messages,
                             )
    phone = forms.CharField(min_length=11,
                             label='手机',
                             widget=wid_text,
                             error_messages=error_messages,
                             )

    gender = forms.ChoiceField(
                            choices=models.UserInfo.gender_choices,
                             label='性别',
                             widget=wid_cho,
                             error_messages=error_messages,
                             )




    #局部钩子,在源码中规定函数的命名方法（clean_字段名）
    def clean_user_name(self):
        # 当定义字段时的规则判断完成时会把通过的字段放在cleaned_data中,这里我们将name取出来进行判断是否纯数字
        val = self.cleaned_data.get("user_name")

        if models.UserInfo.objects.filter(username=val).first():
            raise ValidationError('该用户已被注册....')
        if not val.isdigit():

            return val
        else:
            #校验失败抛出错误 在错误字典（errors）中添加  'name':'错误信息'这样一个键值对
            raise ValidationError("用户名不能是纯数字!")



    def clean_pwd(self):
        val=self.cleaned_data.get('pwd')
        if not val.isdigit():
            return val
        else:
            raise ValidationError('密码不能纯数字')

    # 全局钩子
    def clean(self):
        pwd = self.cleaned_data.get("pwd")
        r_pwd = self.cleaned_data.get("r_pwd")
        if pwd and r_pwd:
            if pwd == r_pwd:
                return self.cleaned_data
            else:
                # 如果验证没有通过,会在错误字典（errors）中添加 '__all__':'错误信息' 这样的一个键值对
                raise ValidationError('两次密码不一致!')
        else:
            return self.cleaned_data


class AddGoodsForm(forms.Form):

    name=forms.CharField(
                              label='商品名称',
                              widget=wid_text,
                              error_messages=error_messages,
                         )
    price=forms.FloatField(
                        label='商品价格',
                        widget=wid_text,
                        error_messages=error_messages,)

    stock=forms.IntegerField(
                          label='商品库存',
                          widget=wid_text,
                          error_messages=error_messages,)


    SELVALUE =models.GoodsClass.objects.all().values_list('pk','title')

    goodsclass = forms.CharField(label='商品类别',max_length=10,widget=forms.widgets.Select(choices=SELVALUE,attrs={"class":"form-control"}))

    goods_details = forms.CharField(label='商品详情',widget=forms.widgets.Textarea(attrs={'id':'content'}))




    def clean_stock(self):
        val=self.cleaned_data.get('stock')

        if type(val) == float or type(val) == int:
            return val
        else:
            raise ValidationError('库存必须整数。。')
    def clean_price(self):
        val=self.cleaned_data.get('price')


        if type(val) == float or type(val) == int :
            return val
        else:
            raise ValidationError('价格必须整数或者小数。。')

class EditGoods(forms.ModelForm):

    class Meta:
        model = models.Goods  # 具体要操作那个模型
        fields = ['name', 'price','stock','goodsclass','goods_details','user']  # 允许编辑的字段
        widgets = {
            "name": widgets.TextInput(attrs={"class":"form-control"}) , # 还可以自定义属性
            "price": widgets.TextInput(attrs={"class":"form-control"}),  # 还可以自定义属性
            "stock": widgets.TextInput(attrs={"class":"form-control"}) , # 还可以自定义属性
            "goodsclass": widgets.Select(attrs={"class":"form-control"}),  # 还可以自定义属性
            "user": widgets.Select(attrs={"class":"form-control",'style':'display:none'}),  # 还可以自定义属性
            "goods_details": widgets.Textarea(attrs={"class":"form-control",'id':'content'}),  # 还可以自定义属性
        }
        labels = {
            "user": ""
        }

class EditUser(forms.ModelForm):
    class Meta:
        model = models.UserInfo
        fields = ['username','address','email','phone',]
        widgets = {
            "username": widgets.TextInput(attrs={"class": "form-control"}),  # 还可以自定义属性
            "address": widgets.TextInput(attrs={"class": "form-control"}),  # 还可以自定义属性
            "email": widgets.TextInput(attrs={"class": "form-control"}),  # 还可以自定义属性
            "phone": widgets.TextInput(attrs={"class": "form-control"}),  # 还可以自定义属性
            # "username": widgets.TextInput(attrs={"class": "form-control",'style':'display:none'} ),  # 还可以自定义属性
        }
        labels ={
            'username':'用户名'
        }

    def __init__(self, *args, **kwargs):
        super(EditUser, self).__init__(*args, **kwargs)
        self.fields['username'].required = False
        self.fields['address'].required = False
        self.fields['email'].required = False
        self.fields['phone'].required = False
