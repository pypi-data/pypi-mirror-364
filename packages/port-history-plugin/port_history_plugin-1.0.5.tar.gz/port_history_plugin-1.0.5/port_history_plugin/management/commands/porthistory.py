from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from dcim.models import Device, DeviceRole, Site, Interface, Cable, CablePath, CableTermination
from ipam.models import VLAN, IPAddress, Prefix
from port_history_plugin.models import MAConPorts
from port_history_plugin.choices import StatusChoices
from extras.models import JournalEntry
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

import asyncio
import aiosnmp
import re
import logging

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from netutils.interface import canonical_interface_name

User = get_user_model()
user = User.objects.get_or_create(username="FusionInventory")[0]


class BaseCheckPorts():

    def __init__(self):
        PLUGIN_CFG = settings.PLUGINS_CONFIG['port_history_plugin']
        self.COMMUNITY = PLUGIN_CFG['snmp_community']
        self.SWITCHES_ROLE_SLUG = PLUGIN_CFG['switches_role_slug']
        self.ROUTERS_ROLE_SLUG = PLUGIN_CFG['routers_role_slug']
        self.GROUP2TRACK = PLUGIN_CFG['vlan_group_id']
        self.WORKERS = PLUGIN_CFG['workers']
        self.devices = []
        self.device_dict = defaultdict(dict)
        self.devices_list = []
        self.vlans = defaultdict(list)
        self.vlans_objects = defaultdict(list)
        self.role = DeviceRole.objects.filter(slug__in=self.SWITCHES_ROLE_SLUG)
        self.alert_devices = []
        self.skipped_devices_list = []
        self.writable_devices = []
        self.arp = defaultdict(list)
        self.logger = logging.getLogger('django')

    async def bulk_snmp(self, device, oid_list, community):
        oid_results = {}
        try:
            async with aiosnmp.Snmp(
                    host=device,
                    port=161,
                    community=community,
                    timeout=5,
                    retries=3,
                    max_repetitions=10,
            ) as snmp:
                oid_bulk_result = {}
                for oid in oid_list:
                    reply = await snmp.bulk_walk(oid)
                    for index in reply:
                        oid_bulk_result[index.oid] = index.value
                    oid_results[oid] = oid_bulk_result

                return (device, oid_results)

        except Exception as error:
            return (device, error)
        return (device, None)

    async def bulk_snmp_with_semaphore(self, semaphore, function, *args, **kwargs):
        async with semaphore:
            return await function(*args, **kwargs)

    async def async_bulk_snmp(self, devices, oid_list, community, workers):
        semaphore = asyncio.Semaphore(workers)
        coroutines = [
            self.bulk_snmp_with_semaphore(semaphore, self.bulk_snmp, device, oid_list, community)
            for device in devices
        ]
        result = []
        for future in asyncio.as_completed(coroutines):
            result.append(await future)
        return result

    def dec_to_mac(self, dec):
        mac = ''
        for part in dec:
            mac_part = int(str(part), 10)
            mac_part_frmt = hex(mac_part)[2:].zfill(2)
            mac += str(mac_part_frmt).upper()
        return mac

    def get_uptime_switch(self):
        oid_list = ['.1.3.6.1.6.3.10.2.1.3']
        results = asyncio.run(self.async_bulk_snmp(self.devices, oid_list, self.COMMUNITY, self.WORKERS))
        for device_ip, device_result in results:
            if type(device_result) != dict:
                self.logger.warning(f"не удалось получить информацию по SNMP - {device_ip}")
                self.devices.remove(device_ip)  # Remove the device with problematic result
                continue
            for oid, oid_result in device_result.items():
                for uptime in oid_result.values():
                    self.device_dict[device_ip]['uptime'] = uptime
                    boottime = datetime.now() - timedelta(seconds=uptime)
                    self.device_dict[device_ip]['boottime'] = boottime

    def get_base_netbox_data(self):
        nb_devices = Device.objects.filter(role__in=self.role)
        for nb_device in nb_devices:
            if nb_device.primary_ip4:
                primary_ip = str(nb_device.primary_ip4).split('/')[0]
                self.devices.append(primary_ip)
                self.device_dict[primary_ip]['device'] = nb_device
                self.device_dict[primary_ip]['interfaces'] = {}
                self.device_dict[primary_ip]['ifindexes'] = {}
                self.device_dict[primary_ip]['cable'] = {}
                device_interfaces = Interface.objects.filter(device_id=nb_device.id)
                for intf in device_interfaces:
                    self.device_dict[primary_ip]['interfaces'][intf.name] = [intf]
                    self.device_dict[primary_ip]['cable'][intf.name] = {}
                    if len(intf.connected_endpoints) > 0:
                        self.device_dict[primary_ip]['cable'][intf.name]['intf'] = intf.connected_endpoints[0].name
                        self.device_dict[primary_ip]['cable'][intf.name]['device'] = intf.connected_endpoints[
                            0].device.name
                        self.device_dict[primary_ip]['cable'][intf.name]['device_object'] = intf.connected_endpoints[
                            0].device
                        if intf.connected_endpoints[0].mac_address == None:
                            self.device_dict[primary_ip]['cable'][intf.name]['mac'] = ''
                        else:
                            mac = self.dec_to_mac(intf.connected_endpoints[0].mac_address.words)
                            self.device_dict[primary_ip]['cable'][intf.name]['mac'] = mac
                    else:
                        self.device_dict[primary_ip]['cable'][intf.name]['intf'] = ''
                        self.device_dict[primary_ip]['cable'][intf.name]['device'] = ''
                        self.device_dict[primary_ip]['cable'][intf.name]['mac'] = ''

    def get_base_snmp(self):
        oid_list = ['.1.3.6.1.2.1.31.1.1.1.1']
        results = asyncio.run(self.async_bulk_snmp(self.devices, oid_list, self.COMMUNITY, self.WORKERS))
        for device_ip, device_result in results:
            if type(device_result) != dict or 'uptime' not in self.device_dict[device_ip]:
                continue
            for oid, oid_result in device_result.items():
                for index, index_result in oid_result.items():
                    ifindex = index.split('.')[-1]
                    canonical_intf_name = canonical_interface_name(index_result.decode("utf-8"))
                    if canonical_intf_name in self.device_dict[device_ip]['interfaces']:
                        self.device_dict[device_ip]['ifindexes'][ifindex] = {}
                        self.device_dict[device_ip]['ifindexes'][ifindex]['name'] = canonical_intf_name
                        self.device_dict[device_ip]['ifindexes'][ifindex]['connected'] = False

    def get_arp_table(self):
        oid_list = ['.1.3.6.1.2.1.3.1.1.2']
        results = asyncio.run(self.async_bulk_snmp(self.devices, oid_list, self.COMMUNITY, self.WORKERS))
        for device_ip, device_result in results:
            for oid, oid_result in device_result.items():
                for index, index_result in oid_result.items():
                    try:
                        snmp_address = '.'.join(index.split('.')[-4:])
                        snmp_mac = ''.join(["{0:x}".format(int(i)).zfill(2) for i in index_result]).upper()
                        self.arp[snmp_mac] = snmp_address
                    except TypeError:
                        print("The object is not iterable!")

    def get_vlan_table(self):
        oid_list = ['.1.3.6.1.2.1.17.7.1.2.2.1.2']
        vlan_list = []
        results = asyncio.run(self.async_bulk_snmp(self.devices, oid_list, self.COMMUNITY, self.WORKERS))
        for device_ip, device_result in results:
            for oid, oid_result in device_result.items():
                for index, index_result in oid_result.items():
                    snmp_dec_mac_address = '.'.join(index.split('.')[-6:])
                    snmp_mac = self.dec_to_mac(snmp_dec_mac_address.split('.'))
                    snmp_vlan_id = '.'.join(index.split('.')[-7])
                    snmp_vlan_id = snmp_vlan_id.replace('.', '')
                    self.vlans[snmp_mac] = snmp_vlan_id
                    vlan_list.append(snmp_vlan_id)
        unique_vlan_list = list(set(vlan_list))
        if(self.GROUP2TRACK):
            for vlan_id in unique_vlan_list:
                self.vlans_objects[vlan_id] = VLAN.objects.get(vid=vlan_id, group_id=self.GROUP2TRACK)
        else:
            for vlan_id in unique_vlan_list:
                self.vlans_objects[vlan_id] = VLAN.objects.get(vid=vlan_id)

    def get_switch_lldp_neighbours(self):
        oid_list = ['.1.0.8802.1.1.2.1.4.1.1.9']
        results = asyncio.run(self.async_bulk_snmp(self.devices, oid_list, self.COMMUNITY, self.WORKERS))
        for device_ip, device_result in results:
            if type(device_result) != dict or 'uptime' not in self.device_dict[device_ip]:
                continue
            for oid, oid_result in device_result.items():
                for index, index_result in oid_result.items():
                    ifindex = index.split('.')[-2]
                    count_on_port = index.split('.')[-1]
                    if index_result is None:
                        continue
                    dst_system_name = index_result.decode("utf-8")
                    if ifindex in self.device_dict[device_ip]['ifindexes'].keys():
                        # if count_on_port not in self.device_dict[device_ip]['ifindexes'][ifindex].keys():
                        self.device_dict[device_ip]['ifindexes'][ifindex][count_on_port] = {}
                        self.device_dict[device_ip]['ifindexes'][ifindex][count_on_port]['device'] = dst_system_name

        oid_list = ['.1.0.8802.1.1.2.1.4.1.1.7']
        results = asyncio.run(self.async_bulk_snmp(self.devices, oid_list, self.COMMUNITY, self.WORKERS))
        for device_ip, device_result in results:
            if type(device_result) != dict or 'uptime' not in self.device_dict[device_ip]:
                continue
            for oid, oid_result in device_result.items():
                for index, index_result in oid_result.items():
                    ifindex = index.split('.')[-2]
                    count_on_port = index.split('.')[-1]
                    if index_result is None:
                        continue
                    snmp_mac = ''.join(["{0:x}".format(int(i)).zfill(2) for i in index_result]).upper()
                    if ifindex in self.device_dict[device_ip]['ifindexes'].keys():
                        # if count_on_port not in self.device_dict[device_ip]['ifindexes'][ifindex].keys():
                        self.device_dict[device_ip]['ifindexes'][ifindex][count_on_port]['mac'] = snmp_mac
                        if snmp_mac in self.arp.keys():
                            self.device_dict[device_ip]['ifindexes'][ifindex][count_on_port]["ip"] = self.arp[snmp_mac]
                        else:
                            self.device_dict[device_ip]['ifindexes'][ifindex][count_on_port]["ip"] = None
                        if snmp_mac in self.vlans.keys():
                            self.device_dict[device_ip]['ifindexes'][ifindex][count_on_port]["vlan"] = self.vlans[
                                snmp_mac]

    def add_journal_entries(self, item):
        inrf = self.device_dict[item['device_ip']]['interfaces'][item['interface']][0]
        events = JournalEntry.objects.filter(assigned_object_id=inrf.id)
        formatted_mac_address = ':'.join([item['dst_mac'][i:i + 2] for i in range(0, len(item['dst_mac']), 2)]).lower()
        if item['netbox_dst_device'] == '':
            dst_device_name = "UNKNOWN"
        else:
            dst_device_name = item['netbox_dst_device']

        message = f"LLDP neighbor check for device {item['source_device_name']} where endpoint device {dst_device_name} with mac address {formatted_mac_address} has status: {item['check_status']}"
        message_template = "LLDP neighbor check for device"

        if len(events) > 0:
            if len(events) < 10:
                count_lmt = len(events)
            else:
                count_lmt = 10
            for num in range(0, count_lmt):
                if str(events[num].comments).startswith(message_template):
                    if events[num].comments == message:
                        pass
                    else:
                        entry = JournalEntry.objects.create(
                            assigned_object_type=ContentType.objects.get(app_label='dcim', model='interface'),
                            assigned_object_id=inrf.id,
                            comments=message
                        )
                        entry.save()
                    return
        entry = JournalEntry.objects.create(
            assigned_object_type=ContentType.objects.get(app_label='dcim', model='interface'),
            assigned_object_id=inrf.id,
            comments=message
        )
        entry.save()

    def write_to_netbox(self):
        pattern = r'^([0-9A-Fa-f]{2}){6}$'
        for device in self.writable_devices:
            if re.match(pattern, device['dst_mac']):
                self.alert_devices.append(device)

        for item in self.alert_devices:
            print(item)
            MAConPorts.objects.filter(
                interface=self.device_dict[item['device_ip']]['interfaces'][item['interface']][0]).delete()
            try:
                ip_address, ip_created = IPAddress.objects.get_or_create(address=f"{item['dst_ip']}/24")
            except Exception as e:
                self.logger.error(e)
                ip_address = None
            else:
                if (not ip_created):
                    self.logger.info(
                        f'IP address {item["dst_ip"]}/24 already exists.')

            if item['check_status'] == 'passed':
                status = StatusChoices.STATUS_PASSED
            elif item['check_status'] == 'failed':
                status = StatusChoices.STATUS_FAILED
            elif item['check_status'] == 'no_lldp_response':
                status = StatusChoices.STATUS_UNCHECKED
            elif item['check_status'] == 'MAC Mismatch':
                status = StatusChoices.STATUS_MACMISMATCH
            else:
                status = StatusChoices.STATUS_UNKNOWN

            mac, created = MAConPorts.objects.get_or_create(
                interface=self.device_dict[item['device_ip']]['interfaces'][item['interface']][0],
                defaults={
                    'device': self.device_dict[item['device_ip']]['device'],
                    'ipaddress': ip_address,
                    'vlan': self.vlans_objects[item['dst_vlan']] if item['dst_vlan'] in self.vlans_objects else None,
                    'mac': item['dst_mac'],
                    'status': status,
                    'lldp_device': item['dst_device'],
                    'netbox_device': item['netbox_dst_device'],
                }
            )
            mac.save()
            self.add_journal_entries(item)

    def get_skipped_devices(self):
        tmp_device_checked_dict = defaultdict(dict)
        for device_info in self.writable_devices:
            tmp_device_checked_dict[device_info["source_device_name"]][device_info["interface"]] = device_info[
                "netbox_dst_device"]

        for device_ip in self.devices:
            for intf_name, ifindex in self.device_dict[device_ip]['interfaces'].items():
                for intf in ifindex:
                    try:
                        if intf.connected_endpoints:
                            if intf.cf['flag-ignore-mac'] != True:
                                if intf.device.name in tmp_device_checked_dict and intf.name in tmp_device_checked_dict[
                                    intf.device.name]:
                                    pass
                                else:
                                    try:
                                        plugin_record = MAConPorts.objects.filter(
                                            interface=self.device_dict[device_ip]['interfaces'][intf_name][0])
                                        if plugin_record[0].mac == '00:00:00:00:00:00':
                                            self.writable_devices.append({'device_ip': device_ip,
                                                                          'source_device_name': intf.device.name,
                                                                          'interface': intf_name,
                                                                          'num': None,
                                                                          'dst_mac': '000000000000',
                                                                          'dst_device': None,
                                                                          'netbox_dst_device': intf.connected_endpoints[
                                                                              0].device.name,
                                                                          'dst_ip': None,
                                                                          'dst_vlan': None,
                                                                          'check_status': 'no_lldp_response',
                                                                          })
                                    except (IndexError, AttributeError):
                                        print("The MAConPorts object does not exist!")
                                        self.writable_devices.append({'device_ip': device_ip,
                                                                      'source_device_name': intf.device.name,
                                                                      'interface': intf_name,
                                                                      'num': None,
                                                                      'dst_mac': '000000000000',
                                                                      'dst_device': None,
                                                                      'netbox_dst_device': intf.connected_endpoints[
                                                                          0].device.name,
                                                                      'dst_ip': None,
                                                                      'dst_vlan': None,
                                                                      'check_status': 'no_lldp_response',
                                                                      })
                                    except Exception as e:
                                        print(f"An error occurred: {e}")
                            else:
                                try:
                                    MAConPorts.objects.filter(
                                        interface=self.device_dict[device_ip]['interfaces'][intf_name][0]).delete()
                                    entry = JournalEntry.objects.create(
                                        assigned_object_type=ContentType.objects.get(app_label='dcim',
                                                                                     model='interface'),
                                        assigned_object_id=intf.id,
                                        comments=f'MAC verification by the inventory plugin is disabled on the interface {intf_name} {intf.device.name}.'
                                    )
                                    entry.save()
                                except Exception as e:
                                    pass

                    except Exception as e:
                        print(e)

    def format_alert_list(self):
        for device_ip in self.devices:
            for num, ifindex in self.device_dict[device_ip]['ifindexes'].items():
                for cnt_on_port, dst_host_dict in ifindex.items():
                    try:
                        if ('device' and 'mac') in dst_host_dict.keys():
                            intf = self.device_dict[device_ip]['interfaces'][ifindex['name']][0]
                            source_device_name = intf.device.name
                            self.device_dict[device_ip]['ifindexes'][num]['connected'] = True
                            if dst_host_dict['mac'] != self.device_dict[device_ip]['cable'][ifindex['name']]['mac'] and dst_host_dict['device'] != self.device_dict[device_ip]['cable'][ifindex['name']]['device']:
                                status = 'failed'
                            elif dst_host_dict['mac'] != self.device_dict[device_ip]['cable'][ifindex['name']]['mac'] and dst_host_dict['device'] == self.device_dict[device_ip]['cable'][ifindex['name']]['device']:
                                status = 'MAC Mismatch'
                            else:
                                status = 'passed'
                            self.writable_devices.append({'device_ip': device_ip,
                                                          'source_device_name': source_device_name,
                                                          'interface': ifindex['name'],
                                                          'num': num,
                                                          'dst_mac': dst_host_dict['mac'],
                                                          'dst_device': dst_host_dict['device'],
                                                          'netbox_dst_device':
                                                              self.device_dict[device_ip]['cable'][ifindex['name']][
                                                                  'device'],
                                                          'dst_ip': dst_host_dict['ip'],
                                                          'dst_vlan': dst_host_dict['vlan'],
                                                          'check_status': status,
                                                          })

                    except Exception as e:
                        pass

    def check_last_updated(self):
        plugin_records = MAConPorts.objects.all()
        # Iterate through each record
        for record in plugin_records:
            # Get the last updated date
            date1 = record.last_updated
            # Get the current date and time in UTC
            date2 = datetime.now(timezone.utc)
            # Calculate the time difference between the two dates
            delta = date2 - date1
            # Check if the time difference is more than 6 days
            if delta.days > 6:
                if record.status != StatusChoices.STATUS_OBSOLETE:
                    record.status = StatusChoices.STATUS_OBSOLETE
                    record.save(update_fields=['status'])
                    # Create a journal entry to record the status change
                    entry = JournalEntry.objects.create(
                        assigned_object_type=ContentType.objects.get(app_label='dcim', model='interface'),
                        assigned_object_id=record.interface.id,
                        comments=f'{record.netbox_device} device data on {record.interface.name} {record.device.name} has not been updated for 7 or more days.'
                    )
                    # Save the journal entry
                    entry.save()

    def rename_int(self):
        for device in self.devices:
            for intr in self.device_dict[device]['interfaces']:
                intr_obj = self.device_dict[device]['interfaces'][intr][0]
                print(intr_obj.name)
                new_int_name = str(intr_obj.name).replace("swp", "Eth")
                print(new_int_name)
                print(intr_obj.id)
                mod = Interface.objects.get(id=intr_obj.id)
                mod.name = new_int_name
                mod.save()
    
    def clear_obsolete_records(self):
        objects = MAConPorts.objects.filter(status=StatusChoices.STATUS_OBSOLETE)
        for object in objects:
            if(not object.interface.path.is_complete):
                print(f'Will be deleted as obsolete! {object}')
                object.delete()

class Command(BaseCommand):

    def handle(self, *args, **options):
        # ...
        print('Omae wa mou shindeiru, NANI!?')
        help = 'A custom command to trigger port history'
        print('''
        ⣿⣿⣿⣿⣿⣿⣿⡿⡛⠟⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣿⠿⠨⡀⠄⠄⡘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⠿⢁⠼⠊⣱⡃⠄⠈⠹⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⡿⠛⡧⠁⡴⣦⣔⣶⣄⢠⠄⠄⠹⣿⣿⣿⣿⣿⣿⣿⣤⠭⠏⠙⢿⣿⣿⣿⣿⣿
        ⣿⡧⠠⠠⢠⣾⣾⣟⠝⠉⠉⠻⡒⡂⠄⠙⠻⣿⣿⣿⣿⣿⡪⠘⠄⠉⡄⢹⣿⣿⣿⣿
        ⣿⠃⠁⢐⣷⠉⠿⠐⠑⠠⠠⠄⣈⣿⣄⣱⣠⢻⣿⣿⣿⣿⣯⠷⠈⠉⢀⣾⣿⣿⣿⣿
        ⣿⣴⠤⣬⣭⣴⠂⠇⡔⠚⠍⠄⠄⠁⠘⢿⣷⢈⣿⣿⣿⣿⡧⠂⣠⠄⠸⡜⡿⣿⣿⣿
        ⣿⣇⠄⡙⣿⣷⣭⣷⠃⣠⠄⠄⡄⠄⠄⠄⢻⣿⣿⣿⣿⣿⣧⣁⣿⡄⠼⡿⣦⣬⣰⣿
        ⣿⣷⣥⣴⣿⣿⣿⣿⠷⠲⠄⢠⠄⡆⠄⠄⠄⡨⢿⣿⣿⣿⣿⣿⣎⠐⠄⠈⣙⣩⣿⣿
        ⣿⣿⣿⣿⣿⣿⢟⠕⠁⠈⢠⢃⢸⣿⣿⣶⡘⠑⠄⠸⣿⣿⣿⣿⣿⣦⡀⡉⢿⣧⣿⣿
        ⣿⣿⣿⣿⡿⠋⠄⠄⢀⠄⠐⢩⣿⣿⣿⣿⣦⡀⠄⠄⠉⠿⣿⣿⣿⣿⣿⣷⣨⣿⣿⣿
        ⣿⣿⣿⡟⠄⠄⠄⠄⠄⠋⢀⣼⣿⣿⣿⣿⣿⣿⣿⣶⣦⣀⢟⣻⣿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⡆⠆⠄⠠⡀⡀⠄⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⡿⡅⠄⠄⢀⡰⠂⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ''')
        base_expl = BaseCheckPorts()
        base_expl.get_base_netbox_data()  # Получаю ip устройств, которые необходимо мониторить и создаю под эти устройства словари со всеми интерфейсами, маками на них и конечными устройствами
        base_expl.get_uptime_switch()  # Проверяю доступ по SNMP до свича и снимаю его Uptime (Сам uptime вроде нигде не использую)
        base_expl.get_base_snmp()  # Получаю по SNMP все доступные мне интерфейсы + сравниваю есть ли такие интерфейсы в словаре созданный в get_base_netbox_data
        base_expl.get_vlan_table()  # Забираю с коммутатора список вланов и записываю их в отдельный словарь.
        base_expl.get_arp_table()  # Забираю с коммутатора arp таблицу и записываю их в отдельный словарь
        base_expl.get_switch_lldp_neighbours()  # Получаю с коммутатора LLDP соседей (мак, хостнейм) + маплю влан и ip если он есть в арп и влан таблицах.
        base_expl.format_alert_list()  # Присваиваю статус проверки инвентаризации и создаю массив из устройств для записи в нетбокс
        base_expl.get_skipped_devices()  # Доп проверка, которая проверяет те хосты, которые не были найдены по LLDP, но при этом должны мониторится. Добавляя в тот же словарь для записи в нетбокс.
        base_expl.write_to_netbox()  # Обработка полученного списка устройств и запись их в нетбокс
        base_expl.check_last_updated()  # Изменение статуса у устройств, по которым не поступала информация более 7 дней
        base_expl.clear_obsolete_records() # Удаляем все устаревшие записи по статусу = Obsolete


