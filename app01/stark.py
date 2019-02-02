from django.urls import re_path
from django.shortcuts import HttpResponse

from app01 import models
from stark.services.v1 import site
from stark.handler import Handler


class UserInfoHandler(Handler):
    display_list = ['name', 'age', 'email', Handler.edit_display, Handler.del_display]

    @property
    def urls(self):
        if self.prev:
            url_patterns = [
                re_path(r'^%s/list/$' % self.prev, self.list_view, name=self.list_url_name),
                re_path(r'^%s/add/$' % self.prev, self.add_view, name=self.add_url_name),
                re_path(r'^%s/edit/(\d+)' % self.prev, self.edit_view, name=self.edit_url_name),
                re_path(r'^%s/del/(\d+)' % self.prev, self.del_view, name=self.del_url_name)
            ]
        else:
            url_patterns = [
                re_path(r'^list/$', self.list_view, name=self.list_url_name),
                re_path(r'^add/$', self.add_view, name=self.add_url_name),
                re_path(r'^edit/(\d+)$', self.edit_view, name=self.edit_url_name),
                re_path(r'^del/(\d+)$', self.del_view, name=self.del_url_name),
            ]

        return url_patterns, None, None


class DepartmentHandler(Handler):
    display_list = ['id', 'title', Handler.edit_display, Handler.del_display]
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
        return HttpResponse('详情页')


site.register(models.UserInfo, UserInfoHandler)
site.register(models.Department, DepartmentHandler)
site.register(models.UserInfo, UserInfoHandler, prev="private")
