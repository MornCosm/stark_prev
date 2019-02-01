from django.db import models

# Create your models here.


class Department(models.Model):
    """
    部门表
    """
    title = models.CharField(
        verbose_name="部门名称",
        max_length=32
    )

    def __str__(self):
        return self.title


class UserInfo(models.Model):
    """
    用户表
    """
    name = models.CharField(
        verbose_name="姓名",
        max_length=32
    )
    age = models.CharField(
        verbose_name="年龄",
        max_length=3
    )
    email = models.EmailField(
        verbose_name="邮箱",
        max_length=128
    )
    department = models.ForeignKey(verbose_name="部门名称", to=Department, on_delete=models.CASCADE)