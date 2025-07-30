from netbox.plugins import PluginMenuButton, PluginMenuItem

menu_items = (
    PluginMenuItem(
        link = 'plugins:port_history_plugin:history',  # A reverse compatible link to follow.
        link_text = 'MAC and IP on switches ports',  # Text to display to user.
    ),
)