"""Data models for the network manager application"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class WiFiState(Enum):
    """Enum for WiFi states"""

    OFF = "off"
    ON = "on"
    SCANNING = "scanning"
    CONNECTING = "connecting"


@dataclass
class NetworkInfo:
    """Data class for network information"""

    ssid: str
    signal: int
    requires_password: bool
    is_connected: bool = False
    bssid: Optional[str] = None
    frequency: Optional[int] = None
    channel: Optional[int] = None
    rate: Optional[int] = None
    mode: Optional[str] = None
    security: Optional[str] = None

    @classmethod
    def from_wifi_device(cls, wifi_device):
        """Create NetworkInfo from nmcli wifi device"""
        return cls(
            ssid=wifi_device.ssid,
            signal=wifi_device.signal,
            requires_password=bool(wifi_device.security),
            is_connected=wifi_device.in_use,
            bssid=wifi_device.bssid,
            frequency=wifi_device.freq,
            channel=wifi_device.chan,
            rate=wifi_device.rate,
            mode=wifi_device.mode,
            security=wifi_device.security,
        )
