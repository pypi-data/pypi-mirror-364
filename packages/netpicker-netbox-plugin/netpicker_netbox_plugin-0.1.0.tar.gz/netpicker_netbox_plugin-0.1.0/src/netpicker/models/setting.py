from django.db import models
from django.utils.translation import gettext as _
from netbox.models import NetBoxModel


class Setting(NetBoxModel):
    server_url = models.CharField(verbose_name=_("URL"))
    api_key = models.CharField()
    tenant = models.CharField(max_length=250, verbose_name=_("Tenant"))
    last_synced = models.DateTimeField(blank=True, auto_now=True, null=True, editable=False)
    connection_status = models.CharField(max_length=50, editable=False, null=True, default='')

    class Meta:
        verbose_name = "setting"
        verbose_name_plural = "settings"

    def __str__(self):
        return f"{self.server_url}"

    def get_absolute_url(self):
        return '/'

    @property
    def docs_url(self):
        # TODO: Add docs url
        return ""
