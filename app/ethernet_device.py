import nmcli
from typing import Literal
from nmcli.data.device import DeviceDetails


class EthernetDevice:
    device: str
    hwaddr: str
    name: str
    ipaddr: str
    gateway_addr: str
    state: Literal["connected", "disconnected", "unavailable"]

    def __init__(self):
        eth_dev_obj: DeviceDetails

        for dev in nmcli.device.show_all():
            if dev.get("GENERAL.TYPE") == "ethernet":
                eth_dev_obj = dev
                break

        self.parse_data(eth_dev_obj)
    
    def parse_data(self, eth_dev: DeviceDetails) -> None:
        self.device = eth_dev.get("GENERAL.DEVICE")
        self.hwaddr = eth_dev.get("GENERAL.HWADDR")
        self.name = eth_dev.get("GENERAL.CONNECTION")
        self.ipaddr = eth_dev.get("IP4.ADDRESS[1]") or eth_dev.get("IP6.ADDRESS[1]") or "unavailable"
        self.gateway_addr = eth_dev.get("IP4.GATEWAY") or eth_dev.get("IP6.GATEWAY") or "unavailable"

        state: int = int(eth_dev.get("GENERAL.STATE").split(" ")[0])
        if state == 30:
            self.state = "disconnected"
        elif state == 100:
            self.state = "connected"
        else:
            self.state = "unavailable"
