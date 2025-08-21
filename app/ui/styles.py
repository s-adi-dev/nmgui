"""CSS styling for the application"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk

class StyleManager:
    """Handles CSS styling for the application"""

    CSS_STYLES = b"""
    #wifi-label {
        font-weight: bold;
        font-size: 16px;
        min-height: 30px; /* Ensure consistent height */
    }

    #wifi-networks-label {
        font-weight: bold;
        font-size: 14px;
    }

    /* Refresh button styling - minimal and clean */
    #wifi-refresh-button {
        font-size: 13px;
        padding: 6px 12px;
        border-radius: 6px;
        transition: all 0.2s ease;
        color: #2e76e5;
        font-weight: 500;
        background: transparent;
        border: none;
        box-shadow: none;
        min-height: 30px; /* Match WiFi label height */
    }

    #wifi-refresh-button:hover {
        background-color: rgba(46, 118, 229, 0.1);
        color: #1a5fb4;
    }

    #wifi-refresh-button:active {
        background-color: rgba(46, 118, 229, 0.2);
    }

    #wifi-refresh-button:focus {
        outline: none;
    }

    .rescan-in-progress {
        color: #4a90d9;
        animation: pulse 1.5s infinite;
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

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }

    .title-2 {
        font-size: 1.5rem;
        font-weight: 500;
        min-height: 30px; /* Match WiFi label height */
    }

    .title-4 {
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 8px;
        min-height: 28px; /* Consistent height */
    }

    .dim-label {
        opacity: 0.7;
        font-size: 0.9rem;
    }

    .detail-row {
        padding: 8px 0;  /* Reduced from 12px to 8px */
        border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    }

    .detail-row:last-child {
        border-bottom: none;
    }

    scrollbar slider {
        min-width: 6px;
        min-height: 6px;
    }

    /* Improved dialog styling */
    dialog {
        border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }

    dialog headerbar {
        border-top-left-radius: 12px;
        border-top-right-radius: 12px;
    }

    /* Consistent button styling */
    button {
        border-radius: 6px;
        padding: 6px 16px;
        font-weight: 500;
        transition: all 0.2s ease;
        min-height: 30px; /* Match WiFi label height */
    }

    button:hover {
        filter: brightness(0.95);
    }

    button:active {
        filter: brightness(0.9);
    }

    /* Network list item styling */
    #network-button {
        padding: 8px 16px;  /* Fixed typo: was 8x */
        border-radius: 8px;
        transition: all 0.2s ease;
        min-height: 36px; /* Consistent height */
    }

    #network-button:hover {
        background-color: rgba(0, 0, 0, 0.05);
    }

    .more-details-button {
        padding: 8px;  /* Match the reduced padding */
        border-radius: 8px;
        min-width: 36px;
        min-height: 36px; /* Match network button height */
    }

    .more-details-button:hover {
        background-color: rgba(0, 0, 0, 0.05);
    }

    /* Password dialog improvements - ensure consistent height */
    entry {
        padding: 8px 12px;
        border-radius: 6px;
        min-height: 30px; /* Match WiFi label height */
    }

    .password-entry {
        padding: 8px 12px;
        border-radius: 6px;
        min-height: 30px; /* Match WiFi label height */
        margin-top: 8px;
        margin-bottom: 8px;
    }

    /* Separator styling */
    separator {
        background-color: rgba(0, 0, 0, 0.1);
    }
    """

    @classmethod
    def apply_styles(cls):
        """Apply CSS styles to the application"""
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(cls.CSS_STYLES)

        display = Gdk.Display.get_default()
        Gtk.StyleContext.add_provider_for_display(
            display, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
