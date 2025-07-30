from django.db.models import CharField, Q, TextField, Transform

from core.models import ObjectType
from dcim.models import DeviceRole, DeviceType, Manufacturer, Site
from extras.choices import CustomFieldTypeChoices
from extras.models import CustomField
from extras.models.tags import Tag
from .automation import Automation, Job, Log, MappedDevice, NetpickerDevice
from .base import ProxyQuerySet
from .backup import Backup, BackupHistory
from .setting import Setting
from .. import get_config

__all__ = [
    'Automation', 'Backup', 'BackupHistory', 'Job', 'Log', 'MappedDevice', 'NetpickerDevice',
    'ProxyQuerySet', 'Setting', 'post_migration'
]


def ensure_slurpit_tags(*items):
    if (tags := getattr(ensure_slurpit_tags, 'cache', None)) is None:
        tag, _ = Tag.objects.get_or_create(name='slurpit', slug='slurpit',
                                           defaults={'description': 'Slurp\'it onboarded', 'color': 'F09640'})

        dcim_applicable_to = 'device', 'devicerole', 'devicetype', 'manufacturer', 'site'
        ipam_applicable_to = 'iprange', 'prefix'
        netpicker_applicable_to = 'slurpitinitipaddress', 'slurpitinterface', 'slurpitprefix'

        dcim_Q = Q(app_label='dcim', model__in=dcim_applicable_to)
        ipam_Q = Q(app_label='ipam', model__in=ipam_applicable_to)
        slurpit_Q = Q(app_label='netpicker', model__in=netpicker_applicable_to)

        tagged_types = ObjectType.objects.filter(ipam_Q | dcim_Q | slurpit_Q)
        tag.object_types.set(tagged_types.all())
        tags = {tag}
        ensure_slurpit_tags.cache = tags
    for item in items:
        item.tags.set(tags)
    return tags


def create_custom_fields():
    device = ObjectType.objects.get(app_label='dcim', model='device')
    cf, _ = CustomField.objects.get_or_create(
        name='slurpit_hostname',
        defaults={
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "description": "",
            "is_cloneable": True,
            "label": 'Hostname',
            "group_name": "Slurp'it"
        })
    cf.object_types.set({device})

    cf, _ = CustomField.objects.get_or_create(
        name='slurpit_fqdn',
        defaults={
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "description": "",
            "is_cloneable": True,
            "label": 'Fqdn',
            "group_name": "Slurp'it"
        })
    cf.object_types.set({device})

    cf, _ = CustomField.objects.get_or_create(
        name='slurpit_platform',
        defaults={
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "description": "",
            "is_cloneable": True,
            "label": 'Platform',
            "group_name": "Slurp'it",
        })
    cf.object_types.set({device})

    cf, _ = CustomField.objects.get_or_create(
        name='slurpit_manufacturer',
        defaults={
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "description": "",
            "is_cloneable": True,
            "label": 'Manufacturer',
            "group_name": "Slurp'it",
        })
    cf.object_types.set({device})

    cf, _ = CustomField.objects.get_or_create(
        name='slurpit_devicetype',
        defaults={
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "description": "",
            "is_cloneable": True,
            "label": 'Device Type',
            "group_name": "Slurp'it",
        })
    cf.object_types.set({device})

    cf, _ = CustomField.objects.get_or_create(
        name='slurpit_ipv4',
        defaults={
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "description": "",
            "is_cloneable": True,
            "label": 'Ipv4',
            "group_name": "Slurp'it",
        })
    cf.object_types.set({device})

    cf, _ = CustomField.objects.get_or_create(
        name='slurpit_site',
        defaults={
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "description": "",
            "is_cloneable": True,
            "label": 'Site',
            "group_name": "Slurp'it",
        })
    cf.object_types.set({device})


def create_default_data_mapping():
    return
    SlurpitMapping.objects.all().delete()

    mappings = [
        {"source_field": "hostname", "target_field": "device|name"},
        {"source_field": "fqdn", "target_field": "device|primary_ip4"},
        {"source_field": "ipv4", "target_field": "device|primary_ip4"},
        {"source_field": "device_os", "target_field": "device|platform"},
        {"source_field": "device_type", "target_field": "device|device_type"},
    ]
    for mapping in mappings:
        SlurpitMapping.objects.get_or_create(**mapping)


def add_default_mandatory_objects(tags):
    site, _ = Site.objects.get_or_create(**get_config('Site'))
    site.tags.set(tags)

    manu, _ = Manufacturer.objects.get_or_create(**get_config('Manufacturer'))
    manu.tags.set(tags)

    dtype, _ = DeviceType.objects.get_or_create(manufacturer=manu, **get_config('DeviceType'))
    dtype.tags.set(tags)

    role, _ = DeviceRole.objects.get_or_create(**get_config('DeviceRole'))
    role.tags.set(tags)

    create_default_data_mapping()


def post_migration(sender, **kwargs):
    create_custom_fields()
    tags = ensure_slurpit_tags()
    add_default_mandatory_objects(tags)


class LowerCase(Transform):
    lookup_name = "lower"
    function = "LOWER"


CharField.register_lookup(LowerCase)
TextField.register_lookup(LowerCase)
