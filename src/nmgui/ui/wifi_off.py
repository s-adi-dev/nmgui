import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class WiFiOffWidget(Gtk.Box):
    """Widget displayed when WiFi is off"""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, vexpand=True, spacing=24)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.set_name("wifi-off-box")
        self.set_margin_top(20)  # Add top margin to prevent clipping
        self.set_margin_bottom(20)

        # WiFi disabled icon with background circle
        icon_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        icon_container.set_halign(Gtk.Align.CENTER)
        icon_container.set_valign(Gtk.Align.CENTER)
        icon_container.set_size_request(96, 96)

        wifi_off_icon = Gtk.Image.new_from_icon_name("network-wireless-disabled-symbolic")
        wifi_off_icon.set_pixel_size(56)
        wifi_off_icon.set_halign(Gtk.Align.CENTER)
        wifi_off_icon.set_valign(Gtk.Align.CENTER)
        wifi_off_icon.set_opacity(0.6)

        icon_container.append(wifi_off_icon)

        # Message label
        wifi_off_label = Gtk.Label(label="Turn on Wi-Fi to access networks")
        wifi_off_label.set_halign(Gtk.Align.CENTER)
        wifi_off_label.set_name("wifi-off-label")
        wifi_off_label.set_wrap(True)
        wifi_off_label.set_justify(Gtk.Justification.CENTER)
        wifi_off_label.set_max_width_chars(30)

        self.append(icon_container)
        self.append(wifi_off_label)

