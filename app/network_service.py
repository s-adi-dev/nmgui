import os
import re
import time
import nmcli
import subprocess
import shutil
from typing import List, Tuple, Optional

# Import the new NetworkInfo model from models
from models import NetworkInfo

nmcli.disable_use_sudo()
nmcli.set_lang(os.environ.get("LANG") or "C.UTF-8")

class NmcliExtensions:
    """Extended functionalities for nmcli package"""
    
    @staticmethod
    def connect_to_open_or_saved_wifi(device_control_instance, ssid: str) -> None:
        """Connect to a known WiFi network without requiring password"""
        cmd =  ['device', 'wifi', 'connect', ssid]
                
        try:
            result = device_control_instance._syscmd.nmcli(cmd)
            
            failure_patterns = [
                r'Connection activation failed:',
                r'Error: Connection activation failed',
                r'Error: No network with SSID',
                r'Error: Failed to add/activate new connection'
            ]
            
            for pattern in failure_patterns:
                if re.search(pattern, result):
                    raise nmcli._exception.ConnectionActivateFailedException(
                        f'Connection activation failed for {ssid}'
                    )
            
            print(f"Successfully connected to {ssid}")
            
        except nmcli._exception.ConnectionActivateFailedException:
            raise
        except Exception as e:
            print(f"Failed to connect to {ssid}: {e}")
            raise
    
    @staticmethod
    def wifi_force_rescan(device_control_instance) -> bool:
        """Force a WiFi rescan to refresh available networks"""
        cmd = ['device', 'wifi', 'list', '--rescan', 'yes']
        
                
        try:
            device_control_instance._syscmd.nmcli(cmd)
            print("WiFi rescan completed successfully")
            return True
        except Exception as e:
            print(f"WiFi rescan failed: {e}")
            raise

class NetworkService:
    """Service class to handle network operations"""
    
    @staticmethod
    def get_wifi_status() -> bool:
        """Check Wi-Fi status"""
        try:
            return nmcli.radio.wifi()
        except Exception as e:
            print(f"Error getting Wi-Fi status: {e}")
            return False
    
    @staticmethod
    def toggle_wifi(state: bool) -> bool:
        """Enable or disable Wi-Fi"""
        try:
            current_state = nmcli.radio.wifi()
            if current_state == state:
                return True
            
            if state:
                nmcli.radio.wifi_on()
            else:
                nmcli.radio.wifi_off()
            return True
        except Exception as e:
            print(f"Error toggling Wi-Fi: {e}")
            return False
    
    @staticmethod
    def scan_networks(force_rescan: bool = True) -> List[NetworkInfo]:
        """Scan for available networks with optional force rescan"""
        networks = []
        try:
            if force_rescan:
                NmcliExtensions.wifi_force_rescan(nmcli.device)
                time.sleep(0.5)  # Allow rescan to complete
            
            for wifi in nmcli.device.wifi():
                if not wifi.ssid:
                    continue
                
                # Use the new NetworkInfo.from_wifi_device method
                network = NetworkInfo.from_wifi_device(wifi)
                networks.append(network)
                
            print(f"Found {len(networks)} networks")
            
        except Exception as e:
            print(f"Error scanning networks: {e}")
        
        return networks

    @staticmethod
    def is_wifi_known(ssid: str) -> bool:
        """Check if WiFi network is already known/saved"""
        try:
            connections = nmcli.connection()
            return any(
                nmcli.connection.show(conn.uuid).get("802-11-wireless.ssid") != None
                and nmcli.connection.show(conn.uuid).get("802-11-wireless.ssid") == ssid
                for conn in connections
            )
        except Exception as e:
            print(f"Error checking known networks: {e}")
            return False

    @staticmethod
    def forget_wifi(ssid: str) -> Tuple[bool, str]:
        """
        Forget a saved WiFi network by SSID.
        
        Args:
            ssid: The SSID of the network to forget
            
        Returns:
            Tuple of (success: bool, message: str)
            Where success indicates if the operation was successful,
            and message provides details about the result or error
        """
        try:
            # First check if the network exists in known connections
            if not NetworkService.is_wifi_known(ssid):
                return False, f"No saved network found with SSID: '{ssid}'"
            
            # Try to delete the connection
            try:
                nmcli.connection.delete(ssid)
                
                # Verify deletion was successful
                if NetworkService.is_wifi_known(ssid):
                    return False, f"Failed to forget network '{ssid}' - still exists after deletion"
                    
                return True, f"Successfully forgot network: '{ssid}'"
                
            except nmcli._exception.ConnectionDeleteException as e:
                # Handle specific nmcli deletion errors
                error_msg = str(e).strip()
                if "no such connection" in error_msg.lower():
                    return False, f"No saved network found with SSID: '{ssid}'"
                return False, f"Failed to forget network '{ssid}': {error_msg}"
                
        except Exception as e:
            error_msg = f"Unexpected error forgetting network '{ssid}': {str(e)}"
            print(error_msg)
            return False, error_msg
    
    @staticmethod
    def connect_to_network(ssid: str, password: Optional[str] = None) -> Tuple[bool, str]:
        """Connect to a network using improved connection method"""
        try:
            if password:
                nmcli.device.wifi_connect(ssid, password)
            else:
                NmcliExtensions.connect_to_open_or_saved_wifi(nmcli.device, ssid)
            
            return True, "Connected successfully"
            
        except nmcli._exception.ConnectionActivateFailedException as e:
            return False, f"Connection activation failed: {str(e)}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    @staticmethod
    def disconnect_network(ssid:str) -> Tuple[bool, str]: 
        """Disconnect to a network using improved disconnection method"""
        try:
            nmcli.connection.down(ssid)
            return True, "Disconnected Successfully"
        except Exception as e:
            return False, f"Connection error: {str(e)}"


    @staticmethod
    def get_wifi_details(ssid: str):
        """Get detailed information about a specific wifi network"""
        try:
            for wifi in nmcli.device.wifi():
                if wifi.ssid == ssid:
                    return NetworkInfo.from_wifi_device(wifi)
            return None
        except Exception as e:
            print(f"Error getting wifi details: {e}")
            return None
    
    @staticmethod
    def check_networkmanager():
        """Check if NetworkManager is available on the system"""
        # Check if nmcli command is available
        if not shutil.which("nmcli"):
            print("Error: NetworkManager is not installed or not available in PATH.")
            print("Please install NetworkManager to use this application.")
            return False
        
        # Check if NetworkManager service is running
        try:
            result = subprocess.run(
                ["nmcli", "general", "status"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                print("Error: NetworkManager is not running.")
                print("Please start the NetworkManager service.")
                return False
        except subprocess.TimeoutExpired:
            print("Error: NetworkManager is not responding.")
            return False
        except Exception as e:
            print(f"Error: Could not check NetworkManager status: {e}")
            return False
        
        return True

