#!/usr/bin/env python3
import gi
import argparse
import sys
from network_service import NetworkService
from ui.main_window import NetworkManagerWindow
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from ui.styles import StyleManager

# Application version
__version__ = "1.0.0"

class NetworkManagerApp(Gtk.Application):
    """Main application class"""

    def __init__(self):
        super().__init__(application_id="com.network.manager")

    def do_activate(self):
        """Application activation"""
        StyleManager.apply_styles()
        win = NetworkManagerWindow(self)
        win.present()

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Network Manager - A GTK4 network management application",
        prog="network-manager"
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    return parser.parse_args()

if __name__ == "__main__":
    try:
        # Parse command line arguments first
        args = parse_arguments()

        # Check if NetworkManager is available before starting the app
        if not NetworkService.check_networkmanager():
            sys.exit(1)

        # If we get here, NetworkManager is available, so start the app
        app = NetworkManagerApp()
        app.run()
    except KeyboardInterrupt:
        print("Application stopped manually.")
    except SystemExit:
        # argparse calls sys.exit() for version/help, let it pass through
        pass
