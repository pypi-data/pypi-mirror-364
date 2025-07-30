import django_tables2 as tables
from netbox.tables import BaseTable, ToggleColumn

from port_history_plugin import models

class PortHistoryTable(BaseTable):
    pk = ToggleColumn()
    device = tables.Column(linkify=True)
    interface = tables.LinkColumn(orderable=False)
    vlan = tables.LinkColumn()
    ipaddress = tables.Column(linkify=True, verbose_name="IPv4 Address")
    status = tables.Column(linkify=False)


    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = models.MAConPorts
        fields = (
            'pk',
            'device',
            'interface',
            'vlan',
            'mac',
            'ipaddress',
            'netbox_device',
            'lldp_device',
            'status',
            'updated',
        )
