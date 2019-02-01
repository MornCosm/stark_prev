from django.db import models

# Create your models here.


class Host(models.Model):
    """
    主机表
    """
    host = models.CharField(
        verbose_name="主机名",
        max_length=64
    )
    IP = models.GenericIPAddressField(
        verbose_name="主机IP",
        protocol="both"
    )
