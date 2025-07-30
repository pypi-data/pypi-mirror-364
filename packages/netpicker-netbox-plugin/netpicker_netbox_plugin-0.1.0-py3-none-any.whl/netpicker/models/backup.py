from django.db import models
from netpicker.models.base import NetpickerModel


class Backup(NetpickerModel):
    id = models.CharField(primary_key=True)
    commit = models.CharField()
    upload_date = models.DateTimeField()
    file_size = models.IntegerField()
    initiator = models.CharField()
    readout_error = models.TextField(null=True)

    device_id: str = None
    ipaddress: str = None
    preview: str = None

    class Meta:
        managed = False

    def get_absolute_url(self):
        return f'javascript:alert({self.id});'


class BackupHistory(NetpickerModel):
    timestamp = models.DateTimeField()
    diff = models.TextField()
    deltas = models.TextField()
