from django import forms

from dcim.models import Region, Site, Device
from ipam.models import VLAN
from utilities.forms.fields import DynamicModelMultipleChoiceField
from extras.forms import CustomFieldFilterForm

from port_history_plugin.models import MAConPorts
from port_history_plugin.choices import StatusChoices

class PortHistoryFilterForm( forms.Form):
    """Filter form to filter searches for MAC."""

    model = MAConPorts
    field_order = ["q", "site", "device_id", "vlan","status"]
    q = forms.CharField(required=False, label="Search MAC")
    status = forms.ChoiceField(
            label="Status",
            choices=StatusChoices.CHOICES,
            required=False
    )

    site = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        to_field_name="slug",
        required=False,
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label="Device",
        #query_params={"site": "$site"},
    )
    vlan = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label="VLAN",
        #query_params={"site": "$site"},
    )