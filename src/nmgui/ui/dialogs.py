"""Dialog components for the application"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

class PasswordDialog:
    """Dialog for entering network password"""

    def __init__(self, parent, ssid: str, callback):
        self.parent = parent
        self.ssid = ssid
        self.callback = callback
        self._create_dialog()

    def _create_dialog(self):
        """Create the password dialog"""
        self.dialog_window = Gtk.Window()
        self.dialog_window.set_title(f"Connect to {self.ssid}")
        self.dialog_window.set_default_size(400, 200)  # Increased size for better UX
        self.dialog_window.set_size_request(300, 180)
        self.dialog_window.set_modal(True)
        self.dialog_window.set_transient_for(self.parent)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content_box.set_margin_top(20)
        content_box.set_margin_bottom(20)
        content_box.set_margin_start(20)
        content_box.set_margin_end(20)

        # Network name with icon
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        # wifi_icon = Gtk.Image.new_from_icon_name("network-wireless-symbolic")
        # wifi_icon.set_pixel_size(24)

        network_label = Gtk.Label(label=f"Enter password for \"{self.ssid}\"")
        network_label.set_halign(Gtk.Align.START)
        network_label.set_wrap(True)
        network_label.set_css_classes(["title-4"])

        # header_box.append(wifi_icon)
        header_box.append(network_label)

        self.password_entry = Gtk.PasswordEntry()
        self.password_entry.set_show_peek_icon(True)
        # Use set_placeholder_text if available, otherwise set_text as fallback
        try:
            self.password_entry.set_placeholder_text("Network password")
        except AttributeError:
            self.password_entry.set_text("")  # Empty text as fallback
        self.password_entry.set_css_classes(["password-entry"])
        self.password_entry.connect("activate", lambda _: self._on_connect_clicked(None))

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(8)

        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", lambda _: self.dialog_window.destroy())

        connect_button = Gtk.Button(label="Connect")
        connect_button.add_css_class("suggested-action")
        connect_button.connect("clicked", self._on_connect_clicked)

        button_box.append(cancel_button)
        button_box.append(connect_button)

        content_box.append(header_box)
        content_box.append(self.password_entry)
        content_box.append(button_box)

        self.dialog_window.set_child(content_box)

    def _on_connect_clicked(self, button):
        """Handle connect button click"""
        password = self.password_entry.get_text()
        self.dialog_window.destroy()
        self.callback(password)

    def show(self):
        """Show the dialog"""
        self.dialog_window.present()
        self.password_entry.grab_focus()

class ConnectionResultDialog:
    """Dialog for showing connection results"""

    @staticmethod
    def show_result(parent, ssid: str, success: bool, message: str):
        """Show connection result dialog"""
        dialog = Gtk.AlertDialog()

        if success:
            dialog.set_message(f"Connected to {ssid}")
            dialog.set_detail("Connection established successfully")
        else:
            dialog.set_message(f"Failed to connect to {ssid}")
            dialog.set_detail(f"Error: {message}")

        dialog.set_modal(True)
        dialog.show(parent)
