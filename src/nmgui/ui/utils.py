"""UI utility functions"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

class UIUtils:
    """Utility functions for UI operations"""

    @staticmethod
    def get_signal_icon_name(signal: int) -> str:
        """Get appropriate signal icon based on signal strength"""
        if signal < 20:
            return "network-wireless-signal-weak-symbolic"
        elif signal < 40:
            return "network-wireless-signal-ok-symbolic"
        elif signal < 60:
            return "network-wireless-signal-good-symbolic"
        else:
            return "network-wireless-signal-excellent-symbolic"

    @staticmethod
    def create_signal_icon(signal: int) -> Gtk.Image:
        """Create signal strength icon"""
        icon = Gtk.Image.new_from_icon_name(UIUtils.get_signal_icon_name(signal))
        icon.set_pixel_size(16)
        return icon

    @staticmethod
    def create_click_controller(callback):
        """Create a click controller for a label"""
        controller = Gtk.GestureClick()
        controller.set_button(0)
        controller.connect("pressed", lambda *args: callback())
        return controller

    @staticmethod
    def clear_container(container):
        """Clear all children from a container"""
        child = container.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            container.remove(child)
            child = next_child

    @staticmethod
    def create_detail_row(label: str, value: str, icon_name: str = None) -> Gtk.Box:
        """Create a consistent detail row with optional icon"""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        row.set_margin_start(8)
        row.set_margin_end(8)
        row.set_css_classes(["detail-row"])

        if icon_name:
            icon = Gtk.Image.new_from_icon_name(icon_name)
            icon.set_pixel_size(18)
            icon.set_opacity(0.8)
            row.append(icon)

        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        text_box.set_hexpand(True)

        label_widget = Gtk.Label(label=label)
        label_widget.set_xalign(0)
        label_widget.set_css_classes(["dim-label"])
        label_widget.set_ellipsize(3)  # Ellipsize at end for better performance
        text_box.append(label_widget)

        value_widget = Gtk.Label(label=value)
        value_widget.set_xalign(0)
        value_widget.set_ellipsize(3)  # Ellipsize at end for better performance
        value_widget.set_selectable(True)  # Allow copying values
        text_box.append(value_widget)

        row.append(text_box)
        return row
