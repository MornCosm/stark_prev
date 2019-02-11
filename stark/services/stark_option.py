from django.db.models import ForeignKey, ManyToManyField


class SearchGroupRow(object):
    def __init__(self, request, field_object, queryset_or_choices, option):
        self.query_dict = request.GET
        self.title = field_object.verbose_name
        self.queryset_or_choices = queryset_or_choices
        self.option = option

    def __iter__(self):
        yield """
        <div class="whole">
            %s
        </div>
        <div class="others">
        """ % self.title
        # 编写全部按钮
        query_dict_copy = self.query_dict.copy()
        query_dict_copy._mutable = True

        original_list = query_dict_copy.getlist(self.option.field)
        if not original_list:
            yield "<a class='active' href='?%s'>全部</a>" % query_dict_copy.urlencode()
        else:
            query_dict_copy.pop(self.option.field)
            yield "<a href='?%s'>全部</a>" % query_dict_copy.urlencode()

        # 编写非全部按钮

        for item in self.queryset_or_choices:
            query_dict_copy = self.query_dict.copy()
            query_dict_copy._mutable = True
            text = self.option.get_text(item)
            value = str(self.option.get_value(item))
            if self.option.is_multi:
                multi_list = query_dict_copy.getlist(self.option.field)
                if value in multi_list:
                    multi_list.remove(value)
                    query_dict_copy.setlist(self.option.field, multi_list)
                    yield "<a class='active' href='?%s'>%s</a>" % (query_dict_copy.urlencode(), text)
                else:
                    multi_list.append(value)
                    query_dict_copy.setlist(self.option.field, multi_list)
                    yield "<a href='?%s'>%s</a>" % (query_dict_copy.urlencode(), text)
            else:
                query_dict_copy[self.option.field] = value
                if value in original_list:
                    query_dict_copy.pop(self.option.field)
                    yield "<a class='active' href='?%s'>%s</a>" % (query_dict_copy.urlencode(), text)
                else:
                    yield "<a href='?%s'>%s</a>" % (query_dict_copy.urlencode(), text)
        yield "</div>"


class Option:
    def __init__(self, field, is_multi=False, db_condition=None, group_text_func=None, group_value_func=None):
        self.field = field
        self.is_multi = is_multi
        self.db_condition = db_condition if db_condition else {}
        self.group_text_func = group_text_func
        self.group_value_func = group_value_func
        self.is_choice = False

    def get_db_condition(self, request, *args, **kwargs):
        return self.db_condition

    def get_queryset_or_tuple(self, model_class, request, *args, **kwargs):
        """
        根据字段去获取数据库中的数据
        :param model_class: model类
        :param request: 客户端的请求
        :param args: 其他位置参数
        :param kwargs: 其他关键参数
        :return: 数据库中的数据
        """
        # 1 根据字段名，获取类中的字段对象
        field_object = model_class._meta.get_field(self.field)
        # 2 获取关联数据
        db_condition = self.get_db_condition(request, *args, **kwargs)
        if isinstance(field_object, ForeignKey) or isinstance(field_object, ManyToManyField):
            # FK和M2M,应该去获取其关联表中的数据
            db_condition = self.get_db_condition(request, *args, **kwargs)
            return SearchGroupRow(request, field_object,
                                  field_object.related_model.objects.filter(**db_condition),
                                  self)
        else:
            # 获取choice中的数据
            self.is_choice = True
            return SearchGroupRow(request, field_object, field_object.choices, self)

    def get_text(self, field_rel_object):
        """
        获取字段对象的文本内容
        :param field_rel_object:
        :return:
        """
        if self.group_text_func:
            return self.group_text_func(field_rel_object)

        if self.is_choice:
            return field_rel_object[1]

        return str(field_rel_object)

    def get_value(self, field_rel_object):
        if self.group_value_func:
            return self.group_value_func(field_rel_object)

        if self.is_choice:
            return field_rel_object[0]

        return field_rel_object.pk
