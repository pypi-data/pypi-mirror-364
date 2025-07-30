from django.shortcuts import render
from netbox.views import generic
from django.core.management.base import BaseCommand
#from django.views import generic
from port_history_plugin import models, tables, filters, forms



class PortHistoryView(generic.ObjectListView):
    """Показывает MAC и IP адреса на портах"""
    queryset = models.MAConPorts.objects.all()
    table = tables.PortHistoryTable
    filterset = filters.PortHistoryFilterSet
    filterset_form = forms.PortHistoryFilterForm
    action_buttons = ()