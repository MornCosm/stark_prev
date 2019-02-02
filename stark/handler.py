from types import FunctionType

from django.shortcuts import render, reverse
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
    display_list = []
    per_page = 1
    has_add_btn = True

    def __init__(self, site, model_class, prev=None):
        self.site = site
        self.model_class = model_class
        self.app_label, self.model_name = model_class._meta.app_label, model_class._meta.model_name
        self.prev = prev

    def edit_display(self, obj=None, is_header=None):
        """
        自定义页面显示的列（表头和内容）
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return "编辑"
        name = "%s:%s" % (self.site.namespace, self.edit_url_name,)
        return mark_safe('<a href="%s">编辑</a>' % reverse(name, args=(obj.pk, )))

    def del_display(self, obj=None, is_header=None):
        if is_header:
            return "删除"
        name = "%s:%s" % (self.site.namespace, self.del_url_name,)
        return mark_safe('<a href="%s">删除</a>' % reverse(name, args=(obj.pk, )))

    def get_display_list(self):
        """
        获取页面上应该显示的列，预留的自定义扩展，例如：以后根据用户的不同显示不同的列
        :return:
        """
        value = []
        value.extend(self.display_list)
        return value

    def reverse_add_url(self):
        name = "%s:%s" % (self.site.namespace, self.add_url_name)
        base_url = reverse(name)


    def get_add_btn(self):
        if self.has_add_btn:
            return "<a class='btn btn-primary' href='%s'>添加</a>" % self.reverse_add_url()
        return None

    def list_view(self, request):
        """
        列表页面
        :param request:
        :return:
        """
        # ########## 1. 处理分页 ##########
        all_count = self.model_class.objects.all().count()
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
        table_body_data = self.model_class.objects.all()[pager.start:pager.end]
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
        return render(request, "stark/list.html", locals())

    def add_view(self, request):
        pass

    def edit_view(self, request, pk):
        pass

    def del_view(self, request, pk):
        pass

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
                re_path(r'%s/list/$' % self.prev, self.list_view,
                        name=self.list_url_name)),
            url_patterns.append(re_path(r'%s/add/$' % self.prev, self.add_view,
                                        name=self.add_url_name)),
            url_patterns.append(
                re_path(r'%s/edit/(\d+)$' % self.prev, self.edit_view,
                        name=self.edit_url_name)),
            url_patterns.append(
                re_path(r'%s/del/(\d+)$' % self.prev, self.del_view,
                        name=self.del_url_name)),
            url_patterns.extend(self.extra_url)
        else:
            url_patterns.append(
                re_path(r'list/$', self.list_view,
                        name=self.list_url_name)),
            url_patterns.append(re_path(r'add/$', self.add_view,
                                        name=self.add_url_name)),
            url_patterns.append(
                re_path(r'edit/(\d+)$', self.edit_view,
                        name=self.edit_url_name)),
            url_patterns.append(
                re_path(r'del/(\d+)$', self.del_view,
                        name=self.del_url_name)),
            url_patterns.extend(self.extra_url)
        return url_patterns, None, None

    @property
    def extra_url(self):
        return []

    def wrapper(self, func):
        @functools
