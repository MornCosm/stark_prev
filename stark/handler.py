from django.shortcuts import HttpResponse
from django.urls import re_path


class Handler:
    def __init__(self, model_class, prev=None):
        self.model_class = model_class
        self.app_label, self.model_name = self.model_class._meta.app_label, self.model_class._meta.model_name
        self.prev = prev

    def list_view(self, request):
        """
        列表页面
        :param request:
        :return:
        """
        return HttpResponse('列表页面')

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

        return url_patterns, None, None

    @property
    def extra_url(self):
        return []
