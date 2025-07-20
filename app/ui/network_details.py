"""Network details widget for displaying detailed network information"""

import threading
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
import nmcli

from models import NetworkInfo
from ui.utils import UIUtils
from ui.dialogs import PasswordDialog
from network_service import NetworkService

class NetworkDetailsWidget(Gtk.Box):
    """Widget for displaying detailed network information"""
    
    def __init__(self, network: NetworkInfo, on_back_clicked):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.network = network
        self.on_back_clicked = on_back_clicked
        self.advanced_rows: dict[str, Gtk.Widget] = {}
        
        self._create_header()
        self._create_content()
        self._create_action_buttons()
        self._load_advanced_info()
    
    def _create_header(self):
        """Create header with back button and network name"""
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.set_margin_start(10)
        header_box.set_margin_end(10)
        header_box.set_margin_top(5)
        header_box.set_margin_bottom(15)
        
        back_button = Gtk.Button()
        back_button.set_icon_name("go-previous-symbolic")
        back_button.set_tooltip_text("Back to network list")
        back_button.set_hexpand(False)
        back_button.set_halign(Gtk.Align.START)
        back_button.connect("clicked", lambda _: self.on_back_clicked())
        
        network_name_label = Gtk.Label(label=self.network.ssid)
        network_name_label.set_xalign(0)
        network_name_label.set_hexpand(True)
        network_name_label.set_css_classes(["title-2"])
        
        header_box.append(back_button)
        header_box.append(network_name_label)
        
        self.append(header_box)
        self.append(Gtk.Separator())
    
    def _create_content(self):
        """Create content area with network details"""
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.content_box.set_margin_start(20)
        self.content_box.set_margin_end(20)
        self.content_box.set_margin_top(15)
        self.content_box.set_margin_bottom(20)
        self.content_box.set_vexpand(True)
        
        # Basic information
        status_text = "Connected" if self.network.is_connected else "Not connected"
        self.status_row = UIUtils.create_detail_row(
            "Network Status", status_text, "network-transmit-receive-symbolic"
        )
        self.content_box.append(self.status_row)
        
        self.signal_row = UIUtils.create_detail_row(
            "Signal Strength", f"{self.network.signal}%",
            UIUtils.get_signal_icon_name(self.network.signal)
        )
        self.content_box.append(self.signal_row)
        
        security_status = "Secured" if self.network.requires_password else "Open"
        security_icon = "security-high-symbolic" if self.network.requires_password else "security-low-symbolic"
        self.security_row = UIUtils.create_detail_row(
            "Security", security_status, security_icon
        )
        self.content_box.append(self.security_row)
        
        # Advanced section
        self.content_box.append(Gtk.Separator())
        
        advanced_header = Gtk.Label(label="Advanced Information")
        advanced_header.set_xalign(0)
        advanced_header.set_css_classes(["title-4"])
        advanced_header.set_margin_top(10)
        self.content_box.append(advanced_header)
        
        # Create advanced detail rows
        self._create_advanced_rows()
        
        scrolled_window = Gtk.ScrolledWindow(vexpand=True)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_child(self.content_box)
        
        self.append(scrolled_window)
    
    def _create_advanced_rows(self):
        """Create advanced information rows"""
        advanced_fields = [
            ("Frequency", "completion-snippet-symbolic"),
            ("Channel", "network-cellular-symbolic"),
            ("BSSID", "network-wired-symbolic"),
            ("Speed", "mail-send-receive-symbolic"),
            ("Mode", "network-workgroup-symbolic"),
            ("Security Type", "security-high-symbolic"),
        ]
        
        for field, icon in advanced_fields:
            row = UIUtils.create_detail_row(field, "Loading...", icon)
            self.advanced_rows[field] = row
            self.content_box.append(row)
    
    def _create_action_buttons(self):
        """Create action buttons (connect/disconnect/forget) at the bottom"""
        # Create a separator before buttons
        self.append(Gtk.Separator())
        
        # Create button container
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_margin_start(20)
        button_box.set_margin_end(20)
        button_box.set_margin_top(15)
        button_box.set_margin_bottom(20)
        button_box.set_homogeneous(True)
        
        # Check if network is known (saved)
        is_known = NetworkService.is_wifi_known(self.network.ssid)
        
        # Join Network button - only show if not connected
        if not self.network.is_connected:
            self.join_button = Gtk.Button(label="Join Network")
            self.join_button.set_css_classes(["suggested-action"])
            self.join_button.connect("clicked", self._on_join_clicked)
            button_box.append(self.join_button)
        
        # Disconnect button - only show if connected
        if self.network.is_connected:
            self.disconnect_button = Gtk.Button(label="Disconnect")
            self.disconnect_button.set_css_classes(["destructive-action"])
            self.disconnect_button.connect("clicked", self._on_disconnect_clicked)
            button_box.append(self.disconnect_button)
        
        # Forget button - only show if network is known/saved
        if is_known:
            self.forget_button = Gtk.Button(label="Forget Network")
            self.forget_button.set_css_classes(["destructive-action"])
            self.forget_button.connect("clicked", self._on_forget_clicked)
            button_box.append(self.forget_button)
        
        # Only append button box if there are buttons to show
        if not self.network.is_connected or is_known:
            self.append(button_box)
    
    def _on_join_clicked(self, button):
        """Handle join network button click"""
        button.set_sensitive(False)
        button.set_label("Connecting...")
        
        # Check if network is already known (has saved password)
        if NetworkService.is_wifi_known(self.network.ssid):
            self._connect_to_network(self.network.ssid)
        elif self.network.requires_password:
            # Show password dialog
            self._show_password_dialog()
        else:
            # Open network, connect directly
            self._connect_to_network(self.network.ssid)
    
    def _show_password_dialog(self):
        """Show password dialog for secured networks""" 
        def on_password_provided(password):
            if password:  # Only connect if password was provided (not empty)
                self._connect_to_network(self.network.ssid, password)
            else:
                # Password was empty or dialog was cancelled, re-enable join button
                if hasattr(self, 'join_button'):
                    self.join_button.set_sensitive(True)
                    self.join_button.set_label("Join Network")
        
        dialog = PasswordDialog(
            self.get_root(), 
            self.network.ssid, 
            on_password_provided
        )
        dialog.show()
    
    def _connect_to_network(self, ssid: str, password: str = None):
        """Connect to a network"""
        def connect_thread():
            success, message = NetworkService.connect_to_network(ssid, password)
            GLib.idle_add(self._connection_complete, success, message)
        
        thread = threading.Thread(target=connect_thread)
        thread.daemon = True
        thread.start()
    
    def _connection_complete(self, success, message):
        """Handle connection completion"""
        if success:
            # Update network status
            self.network.is_connected = True
            self._update_row(self.status_row, "Connected")
            
            # Show success message
            self._show_action_result("Connected", f"Successfully connected to {self.network.ssid}")
            
            # Remove join button and recreate action buttons
            self._recreate_action_buttons()
        else:
            # Show error message
            self._show_action_result("Connection Failed", f"Failed to connect: {message}")
            
            # Re-enable join button
            if hasattr(self, 'join_button'):
                self.join_button.set_sensitive(True)
                self.join_button.set_label("Join Network")
        
        return False
    
    def _on_disconnect_clicked(self, button):
        """Handle disconnect button click"""
        button.set_sensitive(False)
        button.set_label("Disconnecting...")
        
        def disconnect_thread():
            success, message = NetworkService.disconnect_network(self.network.ssid)
            GLib.idle_add(self._disconnect_complete, success, message)
        
        thread = threading.Thread(target=disconnect_thread)
        thread.daemon = True
        thread.start()
    
    def _on_forget_clicked(self, button):
        """Handle forget button click"""
        # Create confirmation dialog
        dialog = Gtk.AlertDialog()
        dialog.set_message(f"Forget '{self.network.ssid}'?")
        dialog.set_detail("This will remove the saved network and its password. You'll need to enter the password again to reconnect.")
        dialog.set_buttons(["Cancel", "Forget"])
        dialog.set_cancel_button(0)
        dialog.set_default_button(1)
        
        def on_response(source, result):
            try:
                response = dialog.choose_finish(result)
                if response == 1:  # Forget button clicked
                    self._forget_network(button)
            except Exception as e:
                print(f"Dialog error: {e}")
        
        dialog.choose(self.get_root(), None, on_response)

    def _forget_network(self, button):
        """Forget the network (disconnect first if connected)"""
        button.set_sensitive(False)
        
        # If network is connected, disconnect first, then forget
        if self.network.is_connected:
            button.set_label("Disconnecting...")
            
            def disconnect_then_forget_thread():
                # First disconnect
                success, message = NetworkService.disconnect_network(self.network.ssid)
                if success:
                    # Update network status
                    self.network.is_connected = False
                    # Then forget
                    success, message = NetworkService.forget_wifi(self.network.ssid)
                    GLib.idle_add(self._forget_complete, success, message, True)  # True indicates disconnection happened
                else:
                    # Disconnect failed, show error
                    GLib.idle_add(self._forget_complete, False, f"Failed to disconnect before forgetting: {message}", False)
            
            thread = threading.Thread(target=disconnect_then_forget_thread)
            thread.daemon = True
            thread.start()
        else:
            # Network not connected, just forget
            button.set_label("Forgetting...")
            
            def forget_thread():
                success, message = NetworkService.forget_wifi(self.network.ssid)
                GLib.idle_add(self._forget_complete, success, message, False)  # False indicates no disconnection
        
            thread = threading.Thread(target=forget_thread)
            thread.daemon = True
            thread.start()

    def _disconnect_complete(self, success, message):
        """Handle disconnect completion"""
        if success:
            # Update network status
            self.network.is_connected = False
            self._update_row(self.status_row, "Not connected")
            
            # Show success message
            self._show_action_result("Disconnected", f"Successfully disconnected from {self.network.ssid}")
            
            # Remove disconnect button and recreate action buttons
            self._recreate_action_buttons()
        else:
            # Show error message
            self._show_action_result("Disconnect Failed", f"Failed to disconnect: {message}")
            
            # Re-enable button
            if hasattr(self, 'disconnect_button'):
                self.disconnect_button.set_sensitive(True)
                self.disconnect_button.set_label("Disconnect")
        
        return False
    
    def _forget_complete(self, success, message, was_disconnected=False):
        """Handle forget completion"""
        if success:
            # Update UI if disconnection happened
            if was_disconnected:
                self._update_row(self.status_row, "Not connected")
            
            # Show success message
            action_text = "disconnected and forgotten" if was_disconnected else "forgotten"
            self._show_action_result("Network Forgotten", f"Successfully {action_text} {self.network.ssid}")
            
            # Remove buttons and recreate action buttons
            self._recreate_action_buttons()
        else:
            # Show error message
            self._show_action_result("Forget Failed", f"Failed to forget network: {message}")
            
            # Re-enable button
            if hasattr(self, 'forget_button'):
                self.forget_button.set_sensitive(True)
                self.forget_button.set_label("Forget Network")
        
        return False
    
    def _show_action_result(self, title, message):
        """Show result of an action"""
        dialog = Gtk.AlertDialog()
        dialog.set_message(title)
        dialog.set_detail(message)
        dialog.set_modal(True)
        dialog.show(self.get_root())
    
    def _recreate_action_buttons(self):
        """Recreate action buttons after network state changes"""
        # Remove the last child if it's a button box
        last_child = self.get_last_child()
        if last_child and isinstance(last_child, Gtk.Box):
            # Check if it contains buttons
            first_button_child = last_child.get_first_child()
            if first_button_child and isinstance(first_button_child, Gtk.Button):
                self.remove(last_child)
                # Also remove separator if it exists
                new_last_child = self.get_last_child()
                if new_last_child and isinstance(new_last_child, Gtk.Separator):
                    self.remove(new_last_child)
        
        # Recreate action buttons
        self._create_action_buttons()
    
    def _load_advanced_info(self):
        """Load advanced network information in background"""
        def load_info_thread():
            try:
                wifi_details = None
                for wifi in nmcli.device.wifi():
                    if wifi.ssid == self.network.ssid:
                        wifi_details = wifi
                        break
                
                GLib.idle_add(self._update_advanced_info, wifi_details)
                
            except Exception as e:
                print(f"Error loading advanced info: {e}")
                GLib.idle_add(self._show_advanced_info_error)
        
        thread = threading.Thread(target=load_info_thread)
        thread.daemon = True
        thread.start()
    
    def _update_advanced_info(self, wifi_details):
        """Update UI with network information"""
        if wifi_details:
            updates = {
                "Frequency": f"{wifi_details.freq/1000:.1f} GHz" if wifi_details.freq else "N/A",
                "Channel": str(wifi_details.chan) if wifi_details.chan else "N/A",
                "BSSID": wifi_details.bssid or "N/A",
                "Speed": f"{wifi_details.rate} Mbps" if wifi_details.rate else "N/A",
                "Mode": wifi_details.mode or "N/A",
                "Security Type": wifi_details.security or "Open"
            }
        else:
            updates = {field: "Not available" for field in self.advanced_rows}
        
        for field, value in updates.items():
            self._update_row(self.advanced_rows[field], value)
    
    def _update_row(self, row, value):
        """Update the value of a detail row"""
        child = row.get_last_child()
        if child and isinstance(child, Gtk.Box):
            value_label = child.get_last_child()
            if value_label and isinstance(value_label, Gtk.Label):
                value_label.set_label(str(value))
    
    def _show_advanced_info_error(self):
        """Show error for advanced info loading"""
        for field in self.advanced_rows:
            self._update_row(self.advanced_rows[field], "Error loading data")
