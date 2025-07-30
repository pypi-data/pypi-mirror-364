from django.contrib.postgres.fields import ArrayField
from django.db.models import BigIntegerField, BooleanField, CASCADE, CharField, DateTimeField, Field, ForeignKey, Model, \
    SET_NULL, TextField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

import dcim.models
from netbox.models import NetBoxModel
from netpicker.models.base import NetpickerModel


class Automation(NetBoxModel):
    pass


class Log(NetpickerModel):
    id = CharField(primary_key=True)
    name = TextField()
    job_name = TextField()
    ipaddress = TextField()
    variables = TextField()
    status = TextField()
    created = DateTimeField()
    exec_at = DateTimeField()
    exec_ns = BigIntegerField()
    initiator = TextField()
    return_value = TextField()
    log = TextField()

    class Meta:
        verbose_name = _('log')
        verbose_name_plural = _('logs')
        managed = False

    def get_absolute_url(self):
        return reverse(f'plugins:{self._meta.app_label}:{self._meta.model_name}', args=[self.pk])


class Job(NetpickerModel):
    id = TextField(primary_key=True)
    name = TextField()
    author = TextField()
    platforms = ArrayField(TextField())
    tags = ArrayField(TextField())
    is_simple = BooleanField()
    commands = ArrayField(TextField())
    signature = Field()

    def get_absolute_url(self):
        return reverse(f'plugins:{self._meta.app_label}:{self._meta.model_name}', args=[self.name])

    def __str__(self):
        return f"Job: {self.name}"

    class Meta:
        managed = False

    def delete(self, *args, **kwargs):
        from netpicker.client import delete_job
        delete_job(self)


class NetpickerDeviceBase(Model):
    ipaddress = CharField()
    tenant = CharField()
    platform = CharField()

    class Meta:
        abstract = True


class MappedDevice(NetpickerDeviceBase):
    ipaddress = CharField()
    tenant = CharField()
    platform = CharField()
    netbox = ForeignKey(dcim.models.Device, on_delete=SET_NULL, related_name='netpickers', null=True)

    class Meta:
        unique_together = ('ipaddress', 'tenant')


class NetpickerDevice(NetpickerDeviceBase):
    pass
