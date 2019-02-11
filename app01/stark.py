from django.urls import re_path
from django.shortcuts import HttpResponse

from app01 import models
from stark.services.v1 import site
from stark.handler import Handler, get_choice_text
from stark.services.stark_option import Option


class UserInfoHandler(Handler):
    display_list = [Handler.checkbox_display, 'name', 'age', get_choice_text('性别', 'gender'), 'email', 'department', Handler.edit_display, Handler.del_display]
    search_list = ['name']
    multi_list = [Handler.multi_delete]
    search_group_list = [
        Option('gender', is_multi=True),
        # Option('department', {'id__gt': 2}),
        Option('department', is_multi=True)
    ]

    @property
    def urls(self):
        if self.prev:
            url_patterns = [
                re_path(r'^%s/list/$' % self.prev, self.wrapper(self.list_view), name=self.list_url_name),
                re_path(r'^%s/add/$' % self.prev, self.wrapper(self.add_view), name=self.add_url_name),
                re_path(r'^%s/edit/(?P<pk>\d+)' % self.prev, self.wrapper(self.edit_view), name=self.edit_url_name),
                re_path(r'^%s/del/(?P<pk>\d+)' % self.prev, self.wrapper(self.del_view), name=self.del_url_name)
            ]
        else:
            url_patterns = [
                re_path(r'^list/$', self.wrapper(self.list_view), name=self.list_url_name),
                re_path(r'^add/$', self.wrapper(self.add_view), name=self.add_url_name),
                re_path(r'^edit/(?P<pk>\d+)$', self.wrapper(self.edit_view), name=self.edit_url_name),
                re_path(r'^del/(?P<pk>\d+)$', self.wrapper(self.del_view), name=self.del_url_name),
            ]

        return url_patterns, None, None


class DepartmentHandler(Handler):
    display_list = [Handler.checkbox_display, 'id', 'title', Handler.edit_display, Handler.del_display]
    multi_list = [Handler.multi_delete]

    @property
    def extra_url(self):
        if self.prev:
            url_patterns = list([
                re_path(r'%s/detail/(?P<pk>\d+)$' % self.prev, self.wrapper(self.detail_view),
                        name='%s_%s_%s_detail' % (self.app_label, self.model_name, self.prev))
            ])
        else:
            url_patterns = list([
                re_path(r'detail/(?P<pk>\d+)$', self.wrapper(self.detail_view),
                        name='%s_%s_detail' % (self.app_label, self.model_name))
            ])
        return url_patterns

    def detail_view(self, request, pk, *args, **kwargs):
        return HttpResponse('详情页')


site.register(models.UserInfo, UserInfoHandler)
site.register(models.Department, DepartmentHandler)
