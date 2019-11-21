from django.db import models


# Create your models here.
class Menu(models.Model):
    title = models.CharField(max_length=32, unique=True, verbose_name='标题')
    icon = models.CharField(max_length=32, verbose_name='图标', null=True, blank=True)
    weight = models.IntegerField(default=1, verbose_name='权重')
    name=models.CharField(max_length=32)

    class Meta:
        verbose_name_plural = '菜单表'
        verbose_name = '菜单表'

    def __str__(self):
        return self.title


class Permission(models.Model):
    """
    权限表
    有关联menu的是二级菜单
    没有关联的不是二级菜单，是不可以做菜单的权限
    """
    title = models.CharField(max_length=32, verbose_name='标题')
    url = models.CharField(max_length=128, verbose_name='权限')
    menu = models.ForeignKey('Menu', null=True, blank=True, verbose_name='菜单')
    parent = models.ForeignKey('Permission', null=True, blank=True, verbose_name='父权限')
    name = models.CharField(max_length=32, null=True, blank=True, unique=True, verbose_name='URL别名')

    class Meta:
        verbose_name_plural = '权限表'
        verbose_name = '权限表'

    def __str__(self):
        return self.title
