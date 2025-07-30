import os

from django.apps import apps
from django.db.models.signals import post_migrate
from django.template import Context, Template
from django.utils.safestring import SafeText

from netbox.plugins import PluginConfig, get_plugin_config

class NetpickerConfig(PluginConfig):
    name = __name__
    verbose_name = "Slurp'it Plugin"
    description = "Sync Slurp'it into NetBox"
    version = '1.1.13'
    base_url = "netpicker"

    default_settings = {
        'DeviceType': {'model': "Slurp'it", 'slug': 'slurpit'},
        'DeviceRole': {'name': "Slurp'it", 'slug': 'slurpit'},
        'Site': {'name': "Slurp'it", 'slug': 'slurpit'},
        'Location': {'name': 'Slurp\'it', 'slug': 'slurpit'},
        'Region': {'name': 'Slurp\'it', 'slug': 'slurpit'},
        'SiteGroup': {'name': 'Slurp\'it', 'slug': 'slurpit'},
        'Rack': {'name': 'Slurp\'it'},
        'ConfigTemplate': {'name': 'Slurp\'it'},
        'Manufacturer': {'name': 'OEM', 'slug': 'oem'},
        'unattended_import': False,
        'version': version
    }

    def logo(self, css_class: str = '', safe: bool = True, **kwargs) -> str:
        if css_class:
            kwargs.setdefault('class', css_class)
        opts = ' '.join((f'{k}="{v}"' for k, v in kwargs.items()))
        tpl = Template(f"""
            {{% load static %}}
            <img src="{{% static '{self.name}/netpicker.svg' %}}" alt="{self.name}" {opts}>""")
        text = tpl.render(Context({}))
        result = SafeText(text) if safe else text
        return result

    def ready(self):
        global netpicker_app
        netpicker_app = self
        from .templatetags import netpicker
        from .models import post_migration
        deps_app = apps.get_app_config("virtualization")
        post_migrate.connect(post_migration, sender=deps_app, weak=False)
        super().ready()


config = NetpickerConfig
netpicker_app: NetpickerConfig | None = None


def get_config(cfg):
    return get_plugin_config(get_config.__module__, cfg)

