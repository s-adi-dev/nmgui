from typing import Callable
import gi

from ui.utils import UIUtils
from ethernet_service import EthernetService, EthernetDetails

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class EthernetDetailsWidget(Gtk.Box):
    content: Gtk.Box
    refresh_label: Gtk.Label
    name_label: Gtk.Label
    spinner: Gtk.Spinner
    switch: Gtk.Switch

    def __init__(self, ethernet_switch: Gtk.Switch):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self.content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.switch = ethernet_switch

        self._create_header()
        self.append(self.content)
        self._show_content()

    def _create_header(self):
        self.refresh_label = Gtk.Label(label="Refresh", name="ethernet-scan-label")
        self.refresh_label.set_cursor_from_name("pointer")
        self.refresh_label.add_controller(self._create_click_controller(self.update))

        self.spinner = Gtk.Spinner()
        self.spinner.set_size_request(20, 20)

        self.name_label = Gtk.Label(
            label=EthernetDetails().name or "Not Connected",
            xalign=0,
            name="ethernet-name-label",
        )

        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.append(self.name_label)
        header_box.append(Gtk.Box(hexpand=True))  # Spacer
        header_box.append(self.spinner)
        header_box.append(self.refresh_label)

        self.append(header_box)

    def _create_click_controller(self, callback: Callable):
        """Create a click controller for a label"""
        controller = Gtk.GestureClick()
        controller.set_button(0)
        controller.connect("pressed", lambda *args: callback())
        return controller

    def _show_content(self):
        if not EthernetService.is_ethernet_available():
            return

        details = EthernetDetails()

        self.content.append(
            UIUtils.create_detail_row(
                "Network Status",
                details.state.title(),
                "network-transmit-receive-symbolic",
            )
        )
        self.content.append(
            UIUtils.create_detail_row(
                "IP Address", details.ipaddr, "network-workgroup-symbolic"
            )
        )
        self.content.append(
            UIUtils.create_detail_row(
                "MAC Address", details.hwaddr, "network-wired-symbolic"
            )
        )

    def _clear_content(self):
        child = self.content.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.content.remove(child)
            child = next_child

    def update(self):
        self.spinner.start()
        self.refresh_label.set_sensitive(False)
        self.refresh_label.add_css_class("rescan-in-progress")

        self.name_label.set_label(EthernetDetails().name or "Not Connected")

        if EthernetService.is_ethernet_available():
            self._clear_content()
            self._show_content()
            self.switch.set_sensitive(True)
        else:
            self._clear_content()
            self.switch.set_active(False)
            self.switch.set_sensitive(False)

        self.spinner.stop()
        self.refresh_label.set_sensitive(True)
        self.refresh_label.remove_css_class("rescan-in-progress")
