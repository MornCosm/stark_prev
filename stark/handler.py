from django.shortcuts import HttpResponse, render
from django.urls import re_path


class Handler:
    display_list = []

    def __init__(self, model_class, prev=None):
        self.model_class = model_class
        self.app_label, self.model_name = self.model_class._meta.app_label, self.model_class._meta.model_name
        self.prev = prev

    def get_display_list(self):
        """
        获取页面上应该显示的列，预留的自定义扩展，例如：以后根据用户的不同显示不同的列
        :return:
        """
        value = []
        value.extend(self.display_list)
        return value

    def list_view(self, request):
        """
        列表页面
        :param request:
        :return:
        """
        display_list = self.get_display_list()
        # 获取表头
        table_header_list = []
        table_body_list = []
        # 获取表中实际数据
        table_body_data = self.model_class.objects.all()
        if display_list:
            for field in display_list:
                table_header_list.append(self.model_class._meta.get_field(field).verbose_name)
            table_body_data = table_body_data.values_list(*self.display_list)
        else:
            for row in table_body_data:
                table_body_list.append([row])
            table_header_list.append(self.model_name)
        return render(request, "list.html", locals())

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
                        name=self.add_url_name)),
            url_patterns.append(re_path(r'%s/add/$' % self.prev, self.add_view,
                                        name=self.add_url_name)),
            url_patterns.append(
                re_path(r'%s/edit/(\d+)$' % self.prev, self.edit_view,
                        name=self.add_url_name)),
            url_patterns.append(
                re_path(r'%s/del/(\d+)$' % self.prev, self.del_view,
                        name=self.add_url_name)),
            url_patterns.extend(self.extra_url)
        else:
            url_patterns.append(
                re_path(r'list/$', self.list_view,
                        name=self.add_url_name)),
            url_patterns.append(re_path(r'add/$', self.add_view,
                                        name=self.add_url_name)),
            url_patterns.append(
                re_path(r'edit/(\d+)$', self.edit_view,
                        name=self.add_url_name)),
            url_patterns.append(
                re_path(r'del/(\d+)$', self.del_view,
                        name=self.add_url_name)),
            url_patterns.extend(self.extra_url)
        return url_patterns, None, None

    @property
    def extra_url(self):
        return []
