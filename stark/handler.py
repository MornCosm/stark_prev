import functools
from types import FunctionType

from django import forms
from django.db.models import Q
from django.http import QueryDict, HttpResponse
from django.shortcuts import render, reverse, redirect
from django.urls import re_path
from django.utils.safestring import mark_safe

from stark.utils.pagination import Pagination


def get_choice_text(title, field):
    """
    对于Stark组件中定义列时，choice如果想要显示中文信息，调用此方法即可。
    :param title: 希望页面显示的表头
    :param field: 字段名称
    :return:
    """

    def inner(self, obj=None, is_header=None):
        if is_header:
            return title
        method = "get_%s_display" % field
        return getattr(obj, method)()

    return inner


class Handler:
    display_list = []  # 要展示的字段列表
    per_page = 10  # 平均每页的记录数，用于分页
    has_add_btn = True  # 是否有添加按钮，默认是true
    model_form_class = None  # 是否有model的form类，默认是使用handler自己的
    order_list = []  # 想要排序的字段
    search_list = []  # 关键字查询涉及的字段
    # search_list = ['title']
    multi_list = []  # 操作列表
    search_group_list = []  # 组合搜索

    def __init__(self, site, model_class, prev=None):
        self.site = site
        self.model_class = model_class
        self.app_label, self.model_name = model_class._meta.app_label, model_class._meta.model_name
        self.prev = prev
        self.request = None

    def edit_display(self, obj=None, is_header=None, *args, **kwargs):
        """
        自定义页面显示的列（表头和内容）
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return "编辑"
        return mark_safe('<a href="%s">编辑</a>' % (self.reverse_type_url('edit', pk=obj.pk)))

    def del_display(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return "删除"
        return mark_safe('<a href="%s">删除</a>' % self.reverse_type_url('del', pk=obj.pk))

    def get_display_list(self):
        """
        获取页面上应该显示的列，预留的自定义扩展，例如：以后根据用户的不同显示不同的列
        :return:
        """
        value = []
        value.extend(self.display_list)
        return value

    """
    def get_display_list(self, has_checkbox=True):
        获取页面上应该显示的列，预留的自定义扩展，例如：以后根据用户的不同显示不同的列
        value = [self.checkbox_display, ] if has_checkbox else []
        value.extend(self.display_list)
        return value
    """

    def checkbox_display(self, obj=None, is_header=None,*args, **kwargs):
        if is_header:
            return "选中"
        return mark_safe('<input type="checkbox" name="pk" value="%s"/>' % obj.pk)

    def get_search_group(self):
        return self.search_group_list

    def reverse_type_url(self, type, *args, **kwargs):
        """
        生成带有原搜索条件的url
        :param type: 操作类型，只能是add， edit， del， 中的一种
        :param args:
        :param kwargs:
        :return:
        """
        name = "%s:%s" % (self.site.namespace, getattr(self, "%s_url_name" % type))
        base_url = reverse(name, args=args, kwargs=kwargs)
        if self.request.GET:
            param = self.request.GET.urlencode()
            new_query_dict = QueryDict()
            new_query_dict._mutable=True
            new_query_dict["_filter"] = param
            reverse_url = "%s?%s" % (base_url, new_query_dict.urlencode())
        else:
            reverse_url = base_url
        return reverse_url

    def reverse_list_url(self):
        name = "%s:%s" % (self.site.namespace, self.list_url_name,)
        base_url = reverse(name)
        param = self.request.GET.get('_filter')
        if not param:
            return base_url
        return "%s?%s" % (base_url, param,)

    def get_add_btn(self):
        if self.has_add_btn:
            return "<a class='btn btn-primary' href='%s'>添加</a>" % self.reverse_type_url(type='add')
        return None

    def orders_list(self):
        """
        获取的某种顺序的记录列表，默认是id倒序排列
        :return:
        """
        return self.order_list or ['-id', ]

    def get_search_list(self):
        """
        关键字查询列表
        :return:
        """
        return self.search_list

    def get_search_group_condition(self, request):
        group_condition = {}
        # ?gender=1&department=2
        for option in self.get_search_group():
            original_list = request.GET.getlist(option.field)
            if not original_list:
                continue
            group_condition["%s__in" % option.field] = original_list
        return group_condition




    def get_multi_list(self):
        """
        批量操作列表
        :return:
        """
        return self.multi_list

    def multi_delete(self, request, *args, **kwargs):
        """
        批量删除
        :param request:
        :return:
        """
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(pk__in=pk_list).delete()

    multi_delete.text = "批量删除"

    def list_view(self, request, *args, **kwargs):
        """
        列表页面
        :param request:
        :return:
        """
        # ########## 批量操作   ########
        multi_list = self.get_multi_list()
        multi_dict = {func.__name__: func.text for func in multi_list}
        if request.method == "POST":
            multi_action = request.POST.get("action")
            if multi_action and multi_action in multi_dict:
                multi_action = getattr(self, multi_action)(request, *args, **kwargs)
                if multi_action:
                    return multi_action
        # ########## 搜索 ########
        # 1 关键字搜索
        search_list = self.get_search_list()
        search_value = request.GET.get('query', '')
        conn = Q()
        conn.connector = 'OR'
        if search_value:
            for item in search_list:
                conn.children.append((item, search_value))
        # 2 组合搜索
        search_group_rows = []
        search_group = self.get_search_group()
        for option_object in search_group:
            row = option_object.get_queryset_or_tuple(self.model_class, request, *args, **kwargs)
            search_group_rows.append(row)
        group_condition = self.get_search_group_condition(request)
        # ########## 1. 获取所有数据####
        queryset = self.model_class.objects.all().filter(conn).filter(**group_condition)
        # ########## 2. 排序##########
        order_list = self.orders_list()
        queryset = queryset.order_by(*order_list)
        # ########## 3. 处理分页 ##########
        all_count = queryset.count()
        base_url = request.path_info
        current_page = request.GET.get('page')
        query_params = request.GET.copy()
        pager = Pagination(
            all_count=all_count,
            base_url=base_url,
            current_page=current_page,
            query_params=query_params,
            per_page=self.per_page
        )

        display_list = self.get_display_list()
        # 获取表头
        table_header_list = []
        if display_list:
            for key_or_func in display_list:
                if isinstance(key_or_func, FunctionType):
                    verbose_name = key_or_func(self, None, True)
                else:
                    verbose_name = self.model_class._meta.get_field(key_or_func).verbose_name
                table_header_list.append(verbose_name)
        else:
            table_header_list.append(self.model_class._meta.model_name)

        # 获取表中实际数据
        table_body_data = queryset[pager.start:pager.end]
        table_body_list = []
        for row in table_body_data:
            fields_list = []
            if display_list:
                for key_or_func in display_list:
                    if isinstance(key_or_func, FunctionType):
                        fields_list.append(key_or_func(self, row, False))
                    else:
                        fields_list.append(getattr(row, key_or_func))
            else:
                fields_list.append(row)
            table_body_list.append(fields_list)
        add_btn = None
        if self.has_add_btn:
            add_btn = self.get_add_btn()
        return render(request, "stark/list.html", locals())

    def get_model_form_class(self):
        if self.model_form_class:
            return self.model_form_class

        class StarkModelForm(forms.ModelForm):
            def __init__(self, *args, **kwargs):
                super(StarkModelForm, self).__init__(*args, **kwargs)
                for name, field in self.fields.items():
                    field.widget.attrs["class"] = "form-control"

            class Meta:
                model=self.model_class
                fields="__all__"

        return StarkModelForm

    def save(self, form, is_update=False):
        """
        form表单保存
        :param form:
        :param is_update:
        :return:
        """
        form.save()

    def add_view(self, request):
        model_form_class = self.get_model_form_class()
        if request.method == "GET":
            form = model_form_class()
            return render(request, 'stark/change.html', locals())
        form = model_form_class(request.POST)
        if form.is_valid():
            self.save(form)
            return redirect(to=self.reverse_list_url())
        return render(request, 'stark/change.html', locals())

    def edit_view(self, request, pk):
        model_form_class = self.get_model_form_class()
        edit_obj = self.model_class.objects.get(pk=pk)
        if not edit_obj:
            return HttpResponse("修改的数据不存在，请重新选择!")
        if request.method == "GET":
            form = model_form_class(instance=edit_obj)
            return render(request, "stark/change.html", locals())
        model_form = model_form_class(data=request.POST, instance=edit_obj)
        if model_form.is_valid():
            self.save(model_form)
            return redirect(to=self.reverse_list_url())
        return render(request, 'stark/change.html', locals())



    def del_view(self, request, pk):
        list_url = self.reverse_list_url()
        if request.method == "GET":
            return  render(request, 'stark/delete.html', {'cancel': list_url})
        self.model_class.objects.filter(pk=pk).delete()
        return redirect(to=list_url)

    def get_url_name(self, param):
        if self.prev:
            return '%s_%s_%s_%s' % (self.app_label, self.model_name, self.prev, param)
        return '%s_%s_%s' % (self.app_label, self.model_name, param)

    @property
    def list_url_name(self):

        return self.get_url_name("list")

    @property
    def add_url_name(self):

        return self.get_url_name("add")

    @property
    def edit_url_name(self):
        return self.get_url_name("edit")

    @property
    def del_url_name(self):

        return self.get_url_name("del")

    @property
    def urls(self):
        url_patterns = list()
        if self.prev:
            url_patterns.append(
                re_path(r'%s/list/$' % self.prev, self.wrapper(self.list_view),
                        name=self.list_url_name)),
            url_patterns.append(re_path(r'%s/add/$' % self.prev, self.wrapper(self.add_view),
                                        name=self.add_url_name)),
            url_patterns.append(
                re_path(r'%s/edit/(?P<pk>\d+)$' % self.prev, self.wrapper(self.edit_view),
                        name=self.edit_url_name)),
            url_patterns.append(
                re_path(r'%s/del/(?P<pk>\d+)$' % self.prev, self.wrapper(self.del_view),
                        name=self.del_url_name)),
            url_patterns.extend(self.extra_url)
        else:
            url_patterns.append(
                re_path(r'list/$', self.wrapper(self.list_view),
                        name=self.list_url_name)),
            url_patterns.append(re_path(r'add/$', self.wrapper(self.add_view),
                                        name=self.add_url_name)),
            url_patterns.append(
                re_path(r'edit/(?P<pk>\d+)$', self.wrapper(self.edit_view),
                        name=self.edit_url_name)),
            url_patterns.append(
                re_path(r'del/(?P<pk>\d+)$', self.wrapper(self.del_view),
                        name=self.del_url_name)),
            url_patterns.extend(self.extra_url)
        return url_patterns, None, None

    @property
    def extra_url(self):
        return []

    def wrapper(self, func):
        @functools.wraps(func)
        def inner(request, *args, **kwargs):
            self.request = request
            return func(request, *args, **kwargs)

        return inner
