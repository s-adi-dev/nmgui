import gi
from ui.utils import UIUtils
from models import NetworkInfo, WiFiState

from ui.network_list import NetworkListWidget

gi.require_version("Gtk", "4.0")
from typing import Callable, Optional

from gi.repository import Gdk, GLib, Gtk
from network_service import NetworkService
from ethernet_service import EthernetService, EthernetDetails

from ui.dialogs import PasswordDialog
from ui.network_details import NetworkDetailsWidget
from ui.wifi_off import WiFiOffWidget


class NetworkManagerWindow(Gtk.ApplicationWindow):
    """Main application window"""

    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Network Manager")
        self.set_default_size(450, 350)

        self.current_state = WiFiState.OFF
        self.current_view = "list"  # "list" or "details"
        self._setup_ui()
        self._update_wifi_state(initial_load=True)

        # keypress logic for handling ESC
        key_controller = Gtk.EventControllerKey.new()
        key_controller.connect("key-pressed", self._on_esc_pressed)
        self.add_controller(key_controller)

    def _setup_ui(self):
        """Setup the main UI"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(15)
        main_box.set_margin_bottom(20)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)

        main_box.append(self._create_ethernet_toggle())
        main_box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        main_box.append(self._create_ethernet_header())

        self.ethernet_content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=12
        )
        main_box.append(self.ethernet_content)
        self._show_ethernet_content()

        main_box.append(Gtk.Box(hexpand=True))  # spacer

        main_box.append(self._create_wifi_toggle())
        main_box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True)
        main_box.append(self.content_box)

        self.set_child(main_box)

    def _create_ethernet_toggle(self) -> Gtk.Box:
        """Create the Ethernet toggle section"""
        self.ethernet_switch = Gtk.Switch(valign=Gtk.Align.CENTER)

        self.ethernet_switch.set_sensitive(EthernetService.is_ethernet_available())

        self.ethernet_switch.set_active(EthernetService.get_ethernet_status())
        self.ethernet_switch.connect("state-set", self._on_ethernet_toggled)

        ethernet_label = Gtk.Label(label="Ethernet", xalign=0, name="ethernet-label")

        toggle_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        toggle_box.append(ethernet_label)
        toggle_box.append(Gtk.Box(hexpand=True))  # Spacer
        toggle_box.append(self.ethernet_switch)

        return toggle_box

    def _on_ethernet_toggled(self, switch, state):
        """Handle Ethernet toggle"""
        current_state = EthernetService.get_ethernet_status()

        if current_state == state:
            return

        if EthernetService.toggle_ethernet(state):
            switch.set_active(state)

        self._update_ethernet()

    def _create_ethernet_header(self) -> Gtk.Box:
        self.ethernet_scan_label = Gtk.Label(
            label="Refresh", name="ethernet-scan-label"
        )
        self.ethernet_scan_label.set_cursor_from_name("pointer")
        self.ethernet_scan_label.add_controller(
            self._create_click_controller(self._update_ethernet)
        )

        self.spinner = Gtk.Spinner()
        self.spinner.set_size_request(20, 20)

        self.ethernet_label = Gtk.Label(
            label=EthernetDetails().name or "Not Connected",
            xalign=0,
            name="ethernet-name-label",
        )

        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.append(self.ethernet_label)
        header_box.append(Gtk.Box(hexpand=True))  # Spacer
        header_box.append(self.spinner)
        header_box.append(self.ethernet_scan_label)

        return header_box

    def _create_click_controller(self, callback: Callable):
        """Create a click controller for a label"""
        controller = Gtk.GestureClick()
        controller.set_button(0)
        controller.connect("pressed", lambda *args: callback())
        return controller

    def _clear_ethernet_content(self):
        child = self.ethernet_content.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.ethernet_content.remove(child)
            child = next_child

    def _show_ethernet_content(self):
        if not EthernetService.is_ethernet_available():
            return

        details = EthernetDetails()

        self.ethernet_content.append(
            UIUtils.create_detail_row(
                "Network Status",
                details.state.title(),
                "network-transmit-receive-symbolic",
            )
        )
        self.ethernet_content.append(
            UIUtils.create_detail_row(
                "IP Address", details.ipaddr, "network-workgroup-symbolic"
            )
        )
        self.ethernet_content.append(
            UIUtils.create_detail_row(
                "MAC Address", details.hwaddr, "network-wired-symbolic"
            )
        )

    def _update_ethernet(self):
        self.spinner.start()
        self.ethernet_scan_label.set_sensitive(False)
        self.ethernet_scan_label.add_css_class("rescan-in-progress")

        self.ethernet_label.set_label(EthernetDetails().name or "Not Connected")

        if EthernetService.is_ethernet_available():
            self._clear_ethernet_content()
            self._show_ethernet_content()
            self.ethernet_switch.set_sensitive(True)
        else:
            self._clear_ethernet_content()
            self.ethernet_switch.set_active(False)
            self.ethernet_switch.set_sensitive(False)

        self.spinner.stop()
        self.ethernet_scan_label.set_sensitive(True)
        self.ethernet_scan_label.remove_css_class("rescan-in-progress")

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

        self.network_list = NetworkListWidget(
            self._on_network_selected, self._on_network_details
        )
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
            dialog = PasswordDialog(
                self,
                network.ssid,
                lambda password: self._connect_to_network(network.ssid, password),
            )
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

        if self.current_view == "list" and hasattr(self, "network_list"):
            self.network_list.start_scan()

        return False

    def _on_esc_pressed(self, controller, keyval, keycode, state):
        """Back on details with ESC; quit from main list."""
        try:
            if keyval == Gdk.KEY_Escape:
                # If we're on a details page, go back to the list instead of quitting
                if getattr(self, "current_view", "list") == "details":
                    # (False means: don't force an immediate rescan; adjust if you prefer)
                    self._show_network_list(True)
                    return True

                # Otherwise we're on the main page; quit the app
                app = self.get_application()
                if app is not None:
                    app.quit()
                else:
                    self.close()
                return True
        except Exception as e:
            print(f"Error while closing app using Esc: {e}")
        return False
