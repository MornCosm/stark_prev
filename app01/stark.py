from django.urls import re_path
from django.shortcuts import HttpResponse

from app01 import models
from stark.services.v1 import site
from stark.handler import Handler


class UserInfoHandler(Handler):
    display_list = ['name', 'age', 'email']

    @property
    def urls(self):
        if self.prev:
            url_patterns = [
                re_path(r'^%s/list/$' % self.prev, self.list_view),
                re_path(r'^%s/add/$' % self.prev, self.add_view)
            ]
        else:
            url_patterns = [
                re_path(r'^list/$', self.list_view),
                re_path(r'^add/$', self.add_view)
            ]

        return url_patterns, None, None


class DepartmentHandler(Handler):
    @property
    def extra_url(self):
        if self.prev:
            url_patterns = list([
                re_path(r'%s/detail/(\d+)$' % self.prev, self.detail_view,
                        name='%s_%s_%s_detail' % (self.app_label, self.model_name, self.prev))
            ])
        else:
            url_patterns = list([
                re_path(r'detail/(\d+)$', self.detail_view, name='%s_%s_detail' % (self.app_label, self.model_name))
            ])
        return url_patterns

    def detail_view(self, pk, *args, **kwargs):
        print(pk)
        print(*args)
        print(**kwargs)
        return HttpResponse('详情页')


site.register(models.UserInfo, UserInfoHandler)
site.register(models.Department, DepartmentHandler)
site.register(models.UserInfo, UserInfoHandler, prev="private")
