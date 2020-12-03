from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import JSONField
from simple_history.models import HistoricalRecords

# Create your models here.
from utils.model import BaseModel, SoftModel


class Position(BaseModel):
    name = models.CharField('名称', max_length=32, unique=True)
    description = models.CharField('描述', max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = '职位/岗位'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Permission(SoftModel):
    menu_type_choices = (
        ('目录', '目录'),
        ('菜单', '菜单'),
        ('接口', '接口'),
    )
    name = models.CharField('名称', max_length=30)
    type = models.CharField('类型', max_length=20, choices=menu_type_choices, default='接口')
    is_frame = models.BooleanField('外部链接', default=False)
    sort = models.IntegerField('排序标记', default=1)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='夫')
    method = models.CharField('方法/代号', max_length=50, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '功能权限表'
        verbose_name_plural = verbose_name
        ordering = ['sort']


class Organization(SoftModel):
    organization_type_choices = (
        ('公司', '公司'),
        ('部门', '部门'),
    )
    name = models.CharField('名称', max_length=60)
    type = models.CharField('类型', max_length=20, choices=organization_type_choices, default='部门')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='父')

    class Meta:
        verbose_name = '组织架构'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Role(SoftModel):
    data_type_choices = (
        ('全部', '全部'),
        ('自定义', '自定义'),
        ('同级及以下', '同级及以下'),
        ('本级及以下', '本级及以下'),
        ('本级', '本级'),
        ('仅本人', '仅本人'),
    )
    name = models.CharField('名称', max_length=32, unique=True)
    perms = models.ManyToManyField(Permission, blank=True, verbose_name='功能权限')
    datas = models.CharField('数据权限', max_length=50, choices=data_type_choices, default='本级及以下')
    depts = models.ManyToManyField(Organization, blank=True, verbose_name='权限范围')
    description = models.CharField('描述', max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class User(AbstractUser):
    name = models.CharField('姓名', max_length=20, null=True, blank=True)
    phone = models.CharField('手机号', max_length=11, null=True, blank=True, unique=True)
    avatar = models.CharField('头像', default='/media/default/avatar.png', max_length=1000, null=True, blank=True)
    dept = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='组织')
    position = models.ManyToManyField(Position, blank=True, verbose_name='岗位')
    superior = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='上级主管')
    roles = models.ManyToManyField(Role, blank=True, verbose_name='角色')

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.username


class DictType(SoftModel):
    name = models.CharField('名称', max_length=30)
    code = models.CharField('代号', unique=True, max_length=30)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='父')

    class Meta:
        verbose_name = '字典类型'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Dict(SoftModel):
    name = models.CharField('名称', max_length=1000)
    code = models.CharField('编号', max_length=30, null=True, blank=True)
    fullname = models.CharField('全名', max_length=1000, null=True, blank=True)
    description = models.TextField('描述', blank=True, null=True)
    other = JSONField('其他信息', blank=True, null=True)
    type = models.ForeignKey(DictType, on_delete=models.CASCADE, verbose_name='类型')
    sort = models.IntegerField('排序', default=1)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='父')
    is_used = models.BooleanField('是否有效', default=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = '字典'
        verbose_name_plural = verbose_name
        unique_together = ('name', 'is_used', 'type')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.code and self.code not in self.name:
            self.fullname = self.code + '-' + self.name
        super().save(*args, **kwargs)


class CommonAModel(SoftModel):
    create_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='创建人', related_name='%(class)s_create_by')
    update_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='最后编辑人', related_name='%(class)s_update_by')

    class Meta:
        abstract = True


class CommonBModel(SoftModel):
    create_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='创建人', related_name='%(class)s_create_by')
    update_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='最后编辑人',
        related_name='%(class)s_update_by')
    belong_dept = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='所属部门', related_name='%(class)s_belong_dept')

    class Meta:
        abstract = True


class File(CommonAModel):
    name = models.CharField('名称', max_length=300, null=True, blank=True)
    size = models.IntegerField('文件大小', default=1, null=True, blank=True)
    file = models.FileField('文件', upload_to='%Y/$m/$d')
    type_choices = (
        ('文档', '文档'),
        ('视频', '视频'),
        ('音频', '音频'),
        ('图片', '图片'),
        ('其他', '其他'),
    )
    mime = models.CharField('文件格式', max_length=300, null=True, blank=True)
    type = models.CharField('文件类型', max_length=50, choices=type_choices, default='文档')
    path = models.CharField('地址', max_length=1000, null=True, blank=True)

    class Meta:
        verbose_name = '文件库'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name