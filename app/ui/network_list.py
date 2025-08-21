import time
import threading
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from typing import List, Callable

from network_service import NetworkService
from models import NetworkInfo

class NetworkListWidget(Gtk.Box):
    """Widget for displaying network list with visual rescan feedback"""

    def __init__(self, on_network_selected: Callable, on_network_details: Callable):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.on_network_selected = on_network_selected
        self.on_network_details = on_network_details
        self.is_scanning = False
        self.scan_start_time = None

        self._create_header()
        self._create_network_list()

    def _create_header(self):
        """Create the header with refresh button and spinner"""
        # Create a button instead of a label for better styling and interaction
        self.refresh_button = Gtk.Button()
        self.refresh_button.set_label("Refresh")
        self.refresh_button.set_name("wifi-refresh-button")
        self.refresh_button.connect("clicked", lambda _: self._on_refresh_clicked())

        self.spinner = Gtk.Spinner()
        self.spinner.set_size_request(16, 16)

        networks_label = Gtk.Label(label="Available Networks", xalign=0, name="wifi-networks-label")

        # Create refresh button container to prevent clipping
        refresh_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        refresh_container.set_halign(Gtk.Align.END)
        refresh_container.set_valign(Gtk.Align.CENTER)
        refresh_container.append(self.spinner)
        refresh_container.append(self.refresh_button)

        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header_box.set_margin_top(6)
        header_box.set_margin_bottom(6)
        header_box.append(networks_label)
        header_box.append(Gtk.Box(hexpand=True))  # Spacer
        header_box.append(refresh_container)

        self.append(header_box)

    def _create_network_list(self):
        """Create the scrollable network list"""
        self.network_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, vexpand=True)
        self.network_list_box.set_name("network-list-box")
        self.network_list_box.set_margin_start(0)  # Remove left margin to prevent clipping
        self.network_list_box.set_margin_end(0)

        scrolled_window = Gtk.ScrolledWindow(vexpand=True)
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_child(self.network_list_box)

        self.append(scrolled_window)

    def _create_click_controller(self, callback: Callable):
        """Create a click controller for a label"""
        controller = Gtk.GestureClick()
        controller.set_button(0)
        controller.connect("pressed", lambda *args: callback())
        return controller

    def _on_refresh_clicked(self):
        """Handle refresh button click with visual feedback"""
        if not self.is_scanning:
            self.start_scan()

    def start_scan(self):
        """Start network scanning with visual feedback"""
        if self.is_scanning:
            return

        self.is_scanning = True
        self.scan_start_time = time.time()

        # Update UI for scanning state
        self.spinner.start()
        self.refresh_button.set_sensitive(False)
        self.refresh_button.add_css_class("rescan-in-progress")

        # Clear existing networks
        self._clear_network_list()

        # Show scanning message
        scanning_label = Gtk.Label(label="Scanning for networks...")
        scanning_label.set_margin_top(48)
        scanning_label.set_margin_bottom(48)
        scanning_label.set_name("scanning-label")
        self.network_list_box.append(scanning_label)

        # Start background scan
        thread = threading.Thread(target=self._background_scan)
        thread.daemon = True
        thread.start()

    def _background_scan(self):
        """Background network scanning"""
        try:
            networks = NetworkService.scan_networks(force_rescan=True)
            scan_duration = time.time() - self.scan_start_time if self.scan_start_time else 0

            GLib.idle_add(self._update_network_list, networks, scan_duration)

        except Exception as e:
            print(f"Error during background scan: {e}")
            GLib.idle_add(self._show_scan_error)
        finally:
            GLib.idle_add(self._scan_complete)

    def _update_network_list(self, networks: List[NetworkInfo], scan_duration: float):
        """Update the network list UI with scan results"""
        self._clear_network_list()

        if not networks:
            no_networks_label = Gtk.Label(label="No networks found", xalign=0.5)
            no_networks_label.set_name("no-networks-label")
            no_networks_label.set_margin_top(48)
            no_networks_label.set_margin_bottom(48)
            self.network_list_box.append(no_networks_label)
        else:
            sorted_networks = sorted(networks, key=lambda n: (not n.is_connected, -n.signal))

            for network in sorted_networks:
                network_row = self._create_network_row(network)
                self.network_list_box.append(network_row)

        return False

    def _create_network_row(self, network: NetworkInfo) -> Gtk.Box:
        """Create a row for a network with connect button and more button"""
        row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row_box.set_margin_top(2)
        row_box.set_margin_bottom(2)

        # Main network button
        network_button = self._create_network_button(network)
        network_button.set_hexpand(True)

        # More button
        more_button = Gtk.Button()
        more_button.set_icon_name("go-next-symbolic")
        more_button.set_tooltip_text("More Details")
        more_button.set_css_classes(["more-details-button"])
        more_button.set_valign(Gtk.Align.CENTER)
        more_button.connect("clicked", lambda b, n=network: self.on_network_details(n))

        row_box.append(network_button)
        row_box.append(more_button)

        return row_box

    def _create_network_button(self, network: NetworkInfo) -> Gtk.Button:
        """Create a button for a network"""
        network_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        network_box.set_margin_top(2)  # Reduced margin
        network_box.set_margin_bottom(2)  # Reduced margin

        # Signal strength
        signal_icon = self._get_signal_icon(network.signal)
        network_box.append(signal_icon)

        # Network name
        network_label = Gtk.Label(label=network.ssid, xalign=0, hexpand=True)
        network_box.append(network_label)

        # Connected indicator
        if network.is_connected:
            check_icon = Gtk.Image.new_from_icon_name("object-select-symbolic")
            check_icon.set_pixel_size(16)
            check_icon.set_margin_start(8)
            check_icon.set_name("connected-icon")
            network_box.append(check_icon)

        # Security indicator
        if network.requires_password:
            lock_icon = Gtk.Image.new_from_icon_name("system-lock-screen-symbolic")
            lock_icon.set_pixel_size(16)
            lock_icon.set_margin_start(8)
            network_box.append(lock_icon)

        # Create button
        button = Gtk.Button()
        button.set_name("network-button")
        button.set_child(network_box)

        if network.is_connected:
            button.set_sensitive(False)
            button.add_css_class("connected-network")
        else:
            button.connect("clicked", lambda b, n=network: self.on_network_selected(n))

        return button

    def _get_signal_icon(self, signal: int) -> Gtk.Image:
        """Get signal strength icon based on signal level"""
        if signal < 20:
            icon_name = "network-wireless-signal-weak-symbolic"
        elif signal < 40:
            icon_name = "network-wireless-signal-ok-symbolic"
        elif signal < 60:
            icon_name = "network-wireless-signal-good-symbolic"
        else:
            icon_name = "network-wireless-signal-excellent-symbolic"

        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_pixel_size(16)
        return icon

    def _show_scan_error(self):
        """Show scan error message"""
        self._clear_network_list()
        error_label = Gtk.Label(label="Error scanning networks. Try again.", xalign=0.5)
        error_label.set_name("error-label")
        error_label.set_margin_top(48)
        error_label.set_margin_bottom(48)
        self.network_list_box.append(error_label)
        return False

    def _scan_complete(self):
        """Clean up after scan completes"""
        self.spinner.stop()
        self.refresh_button.set_sensitive(True)
        self.refresh_button.remove_css_class("rescan-in-progress")
        self.is_scanning = False

        return False

    def _clear_network_list(self):
        """Clear all networks from the list"""
        child = self.network_list_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.network_list_box.remove(child)
            child = next_child
