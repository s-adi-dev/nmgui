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
        """parses the information from eth_dev and add to properties"""
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


class EthernetService:
    @staticmethod
    def get_device_details() -> DeviceDetails | None:
        """Get the DeviceDetails object of the ethernet device"""
        # find device with ethernet type
        for dev in nmcli.device.show_all():
            if dev.get("GENERAL.TYPE") == "ethernet":
                return dev

        return None

    @staticmethod
    def get_device() -> str | None:
        """Get the ethernet device's identifier"""
        details = EthernetService.get_device_details()

        if details == None:
            return None

        return details.get("GENERAL.DEVICE")

    @overload
    @staticmethod
    def get_ethernet_status() -> bool:
        """Get the status of the ethernet, True for connected, if not, False. Will always return False if ethernet is not available."""
        pass

    @overload
    @staticmethod
    def get_ethernet_status(details: EthernetDetails) -> bool:
        """Get the status of the ethernet from the details, True for connected, if not, False. Will always return False if ethernet is not available."""
        pass

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
    def is_ethernet_available() -> bool:
        """Check if ethernet is available and able to be connected. This is different from status."""
        pass

    @overload
    @staticmethod
    def is_ethernet_available(details: EthernetDetails) -> bool:
        """Check if ethernet is available and able to be connected from the details. This is different from status."""
        pass

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
