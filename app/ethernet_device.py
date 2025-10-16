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
        # pass device object to parser
        self._parse_data(self.find_device())

    @staticmethod
    def find_device() -> DeviceDetails:
        # find device with ethernet type
        for dev in nmcli.device.show_all():
            if dev.get("GENERAL.TYPE") == "ethernet":
                return dev

    def _parse_data(self, eth_dev: DeviceDetails) -> None:
        # parses the information and add to properties
        self.device = eth_dev.get("GENERAL.DEVICE")
        self.hwaddr = eth_dev.get("GENERAL.HWADDR")
        self.name = eth_dev.get("GENERAL.CONNECTION")
        self.ipaddr = (
            eth_dev.get("IP4.ADDRESS[1]")
            or eth_dev.get("IP6.ADDRESS[1]")
            or "unavailable"
        )
        self.gateway_addr = (
            eth_dev.get("IP4.GATEWAY") or eth_dev.get("IP6.GATEWAY") or "unavailable"
        )

        # the format of GENERAL.STATE is "int (str)", e.g. "100 (connected)"
        state: int = int(eth_dev.get("GENERAL.STATE").split(" ")[0])

        # check for connected and disconnected, the rest is unavailable
        if state == 30:
            self.state = "disconnected"
        elif state == 100:
            self.state = "connected"
        else:
            self.state = "unavailable"

    # not really a scan, but keeping consistent naming with network_service
    def rescan(self) -> None:
        self._parse_data(EthernetDevice.find_device())

    # FIXME: delete later
    def test_print(self):
        print(self.device)
        print(self.name)
        print(self.hwaddr)
        print(self.ipaddr)
        print(self.gateway_addr)
        print(self.state)
