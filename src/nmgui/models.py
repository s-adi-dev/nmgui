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
        # Use getattr with defaults for better performance and error handling
        return cls(
            ssid=getattr(wifi_device, 'ssid', ''),
            signal=getattr(wifi_device, 'signal', 0),
            requires_password=bool(getattr(wifi_device, 'security', None)),
            is_connected=getattr(wifi_device, 'in_use', False),
            bssid=getattr(wifi_device, 'bssid', None),
            frequency=getattr(wifi_device, 'freq', None),
            channel=getattr(wifi_device, 'chan', None),
            rate=getattr(wifi_device, 'rate', None),
            mode=getattr(wifi_device, 'mode', None),
            security=getattr(wifi_device, 'security', None)
        )
