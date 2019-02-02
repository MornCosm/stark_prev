from django.urls import re_path

from stark.handler import Handler


class StarkSite:
    def __init__(self, app_name='stark', namespace='stark'):
        self._registry = []
        self.app_name = app_name
        self.namespace = namespace

    def register(self, model_class, handle_class=Handler, prev=None):
        """

        :param model_class: 是models中数据库表对应的类
        :param handle_class: 处理请求的视图函数所在的类
        :param prev: 前缀
        :return:
        """

        self._registry.append({
            "model_class": model_class,
            "handler": handle_class(self, model_class, prev),
        })

    def get_urls(self):
        url_patterns = []
        for item in self._registry:
            model_class = item['model_class']
            handler = item['handler']
            app_label, model_name = model_class._meta.app_label, model_class._meta.model_name
            url_patterns.append(re_path(r"%s/%s/" % (app_label, model_name), handler.urls))

        return url_patterns

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.namespace


site = StarkSite()
