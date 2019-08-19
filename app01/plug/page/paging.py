from urllib.parse import urlencode
class page():
    def __init__(self,count_all,url,url_params=None,each_count=10,each_page=5,now_page=0):
        '''

        :param count_all: 数据库总行数
        :param now_page: 用户当前点击的页码
        :param url:     使用分页功能的页面
        :param url_params: url 字典类型带的参数
        :param each_count: 每页显示的数据行数
        :param each_page: 显示的分页总数

        '''

        #以下是关于数据行数的操作
        self.count_all = count_all
        self.each_count = each_count
        self.start_count = 0
        self.end_count=count_all


        # 以下是关于页数的变量
        self.each_page = each_page
        self.start_page = 1
        self.end_page = self.count_all


        a, b = divmod(self.count_all, self.each_count)
        if b:
            a += 1

        if a < self.each_page:
            self.each_page = a
        self.page_all = a  # 根据数据库查询出的记录数 来计算需要几页来显示

        try:

            self.now_page = int(now_page)
            if self.now_page<1:
                self.now_page=1
        except Exception as e:
            self.now_page=1

        self.sides=int(self.each_page/2)# 把需要显示的页数对半开

        self.url=url
        self.url_params=url_params



    def end(self):

        if self.now_page*self.each_count>=self.count_all:
            self.end_count=self.count_all
        else:
            self.end_count=self.now_page*self.each_count
        return self.end_count

    def start(self):
        self.start_count = (self.now_page-1) * self.each_count
        return self.start_count

    def start_end_page(self):

        if self.count_all <= self.each_count:
            self.start_page=1
            self.end_page=1
        else:
            if self.now_page <= self.sides:
                self.start_page=1
                self.end_page=self.each_page
            elif self.now_page >= self.page_all-self.sides:
                if self.page_all-self.each_page <1:
                    self.start_page=1
                else:
                    self.start_page=self.page_all-self.each_page+1
                self.end_page=self.page_all
            else:
                if self.now_page-self.sides <1:
                    self.start_page=1
                else:

                    self.start_page=self.now_page-self.sides
                if self.now_page+self.sides >self.page_all:
                    self.end_page=self.page_all
                else:
                    self.end_page=self.now_page+self.sides

    def page_option(self):
        self.start_end_page()
        # if '?'not in self.url:
        #     self.url+='?'
        # else:
        #     self.url+='&'

        page_list=[]
        self.url_params['page']=1
        page_list.append('<a href=%s?%s class="btn btn-default" >首页</a>' % (self.url, self.url_params.urlencode()))
        if(self.now_page-1)<=1:
            self.url_params['page'] = 1
            page_list.append('<a href=%s?%s class="btn  btn-default">上一页</a>' % (self.url, self.url_params.urlencode()))
        else:
            self.url_params['page'] = self.now_page-1
            page_list.append('<a href=%s?%s class="btn  btn-default">上一页</a>'%(self.url, self.url_params.urlencode()))
        for i in range(self.start_page,self.end_page+1):
            self.url_params['page']=i
            if i ==self.now_page:
                p='<a class="active btn  btn-default" href=%s?%s>%s</a>'%(self.url,self.url_params.urlencode(),i)
            else:
                p='<a href=%s?%s class="btn  btn-default">%s</a>'%(self.url,self.url_params.urlencode(),i)
            page_list.append(p)
        if (self.now_page + 1)>=self.page_all:
            self.url_params['page']=self.page_all
            page_list.append('<a href=%s?%s class="btn  btn-default" >下一页</a>' % (self.url,self.url_params.urlencode()))
        else:
            self.url_params['page'] = self.now_page+1
            page_list.append('<a href=%s?%s class="btn  btn-default">下一页</a>' % (self.url, self.url_params.urlencode()))
        self.url_params['page'] = self.page_all
        page_list.append('<a href=%s?%s class="btn  btn-default">尾页</a>' % (self.url, self.url_params.urlencode()))

        return ''.join(page_list)


