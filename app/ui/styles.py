"""CSS styling for the application"""

import gi

gi.require_version("Gtk", "4.0")
import os

from gi.repository import Gdk, Gtk


class StyleManager:
    """Handles CSS styling for the application"""

    CSS_STYLES = b"""
    #wifi-label {
        font-weight: bold;
        font-size: 16px;
    }

    #wifi-networks-label {
        font-weight: bold;
        font-size: 14px;
    }

    #wifi-scan-label {
        font-size: 14px;
    }

    #wifi-scan-label:hover {
        color: #4a90d9;
    }

    #scanning-label {
        font-style: italic;
        color: #888888;
        margin: 10px;
    }

    #error-label {
        color: #cc0000;
        margin: 10px;
    }

    #no-networks-label {
        font-style: italic;
        color: #888888;
        margin: 10px;
    }

    #network-list-box {
        padding: 5px 0;
    }

    .connected-network {
        background-color: rgba(74, 144, 217, 0.1);
    }

    #wifi-off-box {
        margin: 50px;
    }

    #wifi-off-label {
        color: #666666;
        font-size: 14px;
    }

    .rescan-in-progress {
        color: #4a90d9;
        animation: pulse 1.5s infinite;
    }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }

    .title-2 {
        font-size: 1.5rem;
        font-weight: 500;
    }

    .title-4 {
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 8px;
    }

    .dim-label {
        opacity: 0.7;
        font-size: 0.9rem;
    }

    scrollbar slider {
        min-width: 6px;
        min-height: 6px;
    }
    """

    @classmethod
    def apply_styles(cls):
        """Apply CSS styles to the application"""
        css_provider = Gtk.CssProvider()
        # Test if the ~/.config/nmgui/style.css exists
        home_path = os.path.expanduser("~")
        if os.path.exists(f"{home_path}/.config/nmgui/style.css"):
            css_provider.load_from_path(f"{home_path}/.config/nmgui/style.css")
        else:
            css_provider.load_from_data(cls.CSS_STYLES)

        display = Gdk.Display.get_default()
        Gtk.StyleContext.add_provider_for_display(
            display, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
