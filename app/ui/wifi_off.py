import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class WiFiOffWidget(Gtk.Box):
    """Widget displayed when WiFi is off"""
    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, vexpand=True, spacing=30)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.set_name("wifi-off-box")
        
        # WiFi disabled icon
        wifi_off_icon = Gtk.Image.new_from_icon_name("network-wireless-disabled-symbolic")
        wifi_off_icon.set_pixel_size(64)
        wifi_off_icon.set_halign(Gtk.Align.CENTER)
        wifi_off_icon.set_valign(Gtk.Align.CENTER)
        
        # Message label
        wifi_off_label = Gtk.Label(label="Turn on Wi-Fi to Access Networks")
        wifi_off_label.set_halign(Gtk.Align.CENTER)
        wifi_off_label.set_name("wifi-off-label")
        
        self.append(wifi_off_icon)
        self.append(wifi_off_label)

