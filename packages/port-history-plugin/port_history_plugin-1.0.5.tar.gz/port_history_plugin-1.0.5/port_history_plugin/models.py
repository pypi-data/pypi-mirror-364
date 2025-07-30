from django.db import models
from netbox.models import NetBoxModel
from dcim.fields import MACAddressField
from .choices import StatusChoices


class MAConPorts(NetBoxModel):
    updated = models.DateTimeField(auto_now=True)
    mac = MACAddressField(blank=True, verbose_name="MAC Address")
    vlan = models.ForeignKey(
        to="ipam.VLAN",
        on_delete=models.SET_NULL,
        default=None,
        blank=True,
        null=True,
    )
    ipaddress = models.ForeignKey(
        to="ipam.IPAddress",
        on_delete=models.SET_NULL,
        default=None,
        blank=True,
        null=True,
    )
    interface = models.ForeignKey(
        to="dcim.Interface",
        on_delete=models.CASCADE,
        blank=False,
    )
    device = models.ForeignKey(
        to="dcim.Device",
        on_delete=models.CASCADE,
        blank=False,
    )
    status = models.CharField(
        max_length=50,
        choices=StatusChoices,
        default=StatusChoices.STATUS_UNKNOWN
    )

    lldp_device = models.CharField(
        max_length=50,
        default=None,
        blank=True,
        null=True,
    )
    netbox_device = models.CharField(
        max_length=50,
        default=None,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f'{self.interface} - VLAN {self.vlan.vid} MAC {self.mac}'

    class Meta:
        verbose_name_plural = 'MAC and IP on switches ports'