import gi

from models import NetworkInfo, WiFiState
from ui.network_list import NetworkListWidget
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from typing import Optional

from network_service import NetworkService
from ui.network_details import NetworkDetailsWidget
from ui.wifi_off import WiFiOffWidget
from ui.dialogs import PasswordDialog

class NetworkManagerWindow(Gtk.ApplicationWindow):
    """Main application window"""

    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Network Manager")
        self.set_default_size(600, 400)

        self.current_state = WiFiState.OFF
        self.current_view = "list"  # "list" or "details"
        self._setup_ui()
        self._update_wifi_state(initial_load=True)

    def _setup_ui(self):
        """Setup the main UI"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        main_box.set_margin_top(16)
        main_box.set_margin_bottom(16)
        main_box.set_margin_start(16)
        main_box.set_margin_end(16)

        main_box.append(self._create_wifi_toggle())
        main_box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True)
        main_box.append(self.content_box)

        self.set_child(main_box)

    def _create_wifi_toggle(self) -> Gtk.Box:
        """Create the WiFi toggle section"""
        self.wifi_switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        self.wifi_switch.connect("state-set", self._on_wifi_toggled)

        wifi_label = Gtk.Label(label="Wi-Fi", xalign=0, name="wifi-label")

        toggle_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        toggle_box.append(wifi_label)
        toggle_box.append(Gtk.Box(hexpand=True))  # Spacer
        toggle_box.append(self.wifi_switch)

        return toggle_box

    def _on_wifi_toggled(self, switch, state):
        """Handle WiFi toggle"""
        current_state = NetworkService.get_wifi_status()

        if current_state == state:
            return

        if NetworkService.toggle_wifi(state):
            self._update_wifi_state(scan_immediately=state)
        else:
            switch.set_active(current_state)

    def _update_wifi_state(self, scan_immediately=False, initial_load=False):
        """Update the UI based on WiFi state"""
        wifi_status = NetworkService.get_wifi_status()
        self.wifi_switch.set_active(wifi_status)

        if wifi_status:
            self.current_state = WiFiState.ON
            if self.current_view == "list":
                self._show_network_list(scan_immediately or initial_load)
        else:
            self.current_state = WiFiState.OFF
            self.current_view = "list"
            self._show_wifi_off()

    def _show_network_list(self, scan_immediately=False):
        """Show the network list widget"""
        self.current_view = "list"
        self._clear_content()

        self.network_list = NetworkListWidget(self._on_network_selected, self._on_network_details)
        self.content_box.append(self.network_list)

        if scan_immediately:
            GLib.timeout_add(500, lambda: self.network_list.start_scan())

    def _show_network_details(self, network: NetworkInfo):
        """Show the network details widget"""
        self.current_view = "details"
        self._clear_content()

        self.network_details = NetworkDetailsWidget(network, self._on_back_to_list)
        self.content_box.append(self.network_details)

    def _on_back_to_list(self):
        """Handle back button click from details view"""
        self._show_network_list(scan_immediately=True)

    def _show_wifi_off(self):
        """Show the WiFi off widget"""
        self._clear_content()
        wifi_off_widget = WiFiOffWidget()
        self.content_box.append(wifi_off_widget)

    def _clear_content(self):
        """Clear the content area"""
        child = self.content_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.content_box.remove(child)
            child = next_child

    def _on_network_selected(self, network: NetworkInfo):
        """Handle network selection for connection"""
        if NetworkService.is_wifi_known(network.ssid):
            self._connect_to_network(network.ssid)
        elif network.requires_password:
            dialog = PasswordDialog(self, network.ssid,
                                  lambda password: self._connect_to_network(network.ssid, password))
            dialog.show()
        else:
            self._connect_to_network(network.ssid)

    def _on_network_details(self, network: NetworkInfo):
        """Handle network details button click"""
        self._show_network_details(network)

    def _connect_to_network(self, ssid: str, password: Optional[str] = None):
        """Connect to a network"""
        self.current_state = WiFiState.CONNECTING

        def connect_thread():
            success, message = NetworkService.connect_to_network(ssid, password)
            GLib.idle_add(lambda: self._connection_complete(ssid, success, message))

        import threading
        thread = threading.Thread(target=connect_thread)
        thread.daemon = True
        thread.start()

    def _connection_complete(self, ssid: str, success: bool, message: str):
        """Handle connection completion"""
        self.current_state = WiFiState.ON

        dialog = Gtk.AlertDialog()
        if success:
            dialog.set_message(f"Connected to {ssid}")
            dialog.set_detail("Connection established successfully")
        else:
            dialog.set_message(f"Failed to connect to {ssid}")
            dialog.set_detail(f"Error: {message}")

        dialog.set_modal(True)
        dialog.show(self)

        if self.current_view == "list" and hasattr(self, 'network_list'):
            self.network_list.start_scan()

        return False
