from netbox.plugins import PluginConfig
#from core.signals import netbox_database_ready
from port_history_plugin.signals import create_custom_fields_for_porthistory
#from .signals import create_custom_fields_for_porthistory
from django.dispatch import Signal
from django.core.signals import setting_changed
from django.db.models.signals import post_migrate

class NetboxPorthistoryPluginConfig(PluginConfig):
    name = "port_history_plugin"
    verbose_name = "port_history_plugin"
    description = 'Netbox plugin for show port history (last output, MAC on ports)'
    base_url = "port_history_plugin"
    version = '1.0.5'
    author = 'Nikolay Gimozdinov'
    author_email = ''
    default_settings = {
        'min_idle_days': 14,
        'snmp_community': 'public',
        'workers': 50,
    }
    required_settings = ['switches_role_slug', 'routers_role_slug']
    caching_config = {}

    def my_callback(sender, **kwargs):
        print("Request finished!")

    def ready(self):
        super().ready()
        post_migrate.connect(create_custom_fields_for_porthistory, sender=self)


config = NetboxPorthistoryPluginConfig
