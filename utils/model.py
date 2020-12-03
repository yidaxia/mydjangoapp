from django.db import models
from django.db.models.query import QuerySet
import django.utils.timezone as timezone


class SoftDeletableQuerySetMixin(object):
    def delete(self, soft=True):
        if soft:
            self.update(is_deleted=True)
        else:
            return super(SoftDeletableQuerySetMixin, self).delete()


class SoftDeletableQuerySet(SoftDeletableQuerySetMixin, QuerySet):
    pass


class SoftDeletableManagerMixin(object):
    _query_class = SoftDeletableQuerySet

    def get_queryset(self, all=False):
        kwargs = {'model': self.model, 'using': self._db}
        if hasattr(self, '_hints'):
            kwargs['hits'] = self._hints
        if all:
            return self._queryset_class(**kwargs)
        return self._queryset_class(**kwargs).filter(is_deleted=False)


class SoftDeletableManager(SoftDeletableManagerMixin, models.Manager):
    pass


class BaseModel(models.Model):
    create_time = models.DateTimeField(default=timezone.now, verbose_name='创建时间', help_text='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间', help_text='修改时间')
    is_deleted = models.BooleanField(default=False, verbose_name='删除标记', help_text='删除标记')

    class Meta:
        abstract = True


class SoftModel(BaseModel):
    class Meta:
        abstract = True

    object = SoftDeletableManager()

    def delete(self, using=None, soft=True, *args, **kwargs):
        if soft:
            self.is_deleted = True
            self.save(using=using)
        else:
            return super(SoftModel, self).delete(using=using, *args, **kwargs)