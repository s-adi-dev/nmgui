import nmcli
from typing import Literal, overload
from nmcli.data.device import DeviceDetails


class EthernetDetails:
    device: str
    hwaddr: str
    name: str
    ipaddr: str
    gateway_addr: str
    state: Literal["connected", "disconnected", "unavailable"]

    def __init__(self):
        # pass device object to parser
        details = EthernetService.get_device_details()
        if details != None:
            self._parse_data(details)

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
        details = EthernetService.get_device_details()
        if details != None:
            self._parse_data(details)

    # FIXME: delete later
    def test_print(self):
        print(self.device)
        print(self.name)
        print(self.hwaddr)
        print(self.ipaddr)
        print(self.gateway_addr)
        print(self.state)


class EthernetService:

    @staticmethod
    def get_device_details() -> DeviceDetails | None:
        # find device with ethernet type
        for dev in nmcli.device.show_all():
            if dev.get("GENERAL.TYPE") == "ethernet":
                return dev

        return None

    @staticmethod
    def get_device() -> str | None:
        details = EthernetService.get_device_details()

        if details == None:
            return None

        return details.get("GENERAL.DEVICE")

    @overload
    @staticmethod
    def get_ethernet_status() -> bool: ...
    @overload
    @staticmethod
    def get_ethernet_status(details: EthernetDetails) -> bool: ...

    def get_ethernet_status(details: EthernetDetails | None = None) -> bool:
        if details == None:
            details = EthernetService.get_device_details()

            # no ethernet device available
            if details == None:
                return False

            state = int(details.get("GENERAL.STATE").split(" ")[0])

            if state == 100:
                return True

            return False

        # if details is an EthernetDetails object
        else:
            if details.state == "connected":
                return True

            return False

    @overload
    @staticmethod
    def is_ethernet_available() -> bool: ...

    @overload
    @staticmethod
    def is_ethernet_available(details: EthernetDetails) -> bool: ...

    def is_ethernet_available(details: EthernetDetails | None = None) -> bool:
        if details == None:
            details = EthernetService.get_device_details()

            # no ethernet device available
            if details == None:
                return False

            state = int(details.get("GENERAL.STATE").split(" ")[0])

            # if state is disconnected or connected, then its available
            if state == 30 or state == 100:
                return True

            return False

        # if details is an EthernetDetails object
        else:
            if details.state != "unavailable":
                return True

            return False

    @staticmethod
    def toggle_ethernet(state: bool) -> bool:
        """Enable or disable Ethernet"""
        try:
            current_state = EthernetService.get_ethernet_status()
            if current_state == state:
                return True

            if state:
                nmcli._syscmd.nmcli(["device", "connect", EthernetService.get_device()])
            else:
                nmcli._syscmd.nmcli(
                    ["device", "disconnect", EthernetService.get_device()]
                )
            return True
        except Exception as e:
            print(f"Error toggling Ethernet: {e}")
            return False
