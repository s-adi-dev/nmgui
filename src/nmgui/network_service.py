import re
import time
import nmcli
import subprocess
import shutil
from typing import List, Tuple, Optional

# Import the new NetworkInfo model from models
from nmgui.models import NetworkInfo

nmcli.disable_use_sudo()

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
    
    # Cache for network scan results with optimized duration
    _scan_cache = None
    _last_scan_time = 0
    _scan_cache_duration = 1.5  # Balanced cache duration for responsiveness vs. freshness
    _last_connection_change = 0  # Track when connections were last modified
    
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
        """Scan for available networks with intelligent caching"""
        current_time = time.time()
        
        # If we're not forcing a rescan, check if cache is still valid
        if not force_rescan and NetworkService._scan_cache is not None:
            # Cache is valid if:
            # 1. It's not expired (within cache duration)
            # 2. No connection changes have happened since last scan
            cache_age = current_time - NetworkService._last_scan_time
            connection_change_age = current_time - NetworkService._last_connection_change
            
            if (cache_age < NetworkService._scan_cache_duration and 
                connection_change_age > cache_age):
                print("Using cached network scan results")
                return NetworkService._scan_cache
        
        networks = []
        try:
            if force_rescan:
                # Use async rescan for better performance
                NmcliExtensions.wifi_force_rescan(nmcli.device)
                # No sleep needed for async operation
            
            # Use list comprehension for faster processing
            networks = [
                NetworkInfo.from_wifi_device(wifi)
                for wifi in nmcli.device.wifi()
                if wifi.ssid
            ]
            
            print(f"Found {len(networks)} networks")
            
            # Update cache
            NetworkService._scan_cache = networks
            NetworkService._last_scan_time = current_time
            
        except Exception as e:
            print(f"Error scanning networks: {e}")
        
        return networks

    @staticmethod
    def is_wifi_known(ssid: str) -> bool:
        """Check if WiFi network is already known/saved"""
        try:
            connections = nmcli.connection()
            return any(conn.name == ssid for conn in connections)
        except Exception as e:
            print(f"Error checking known networks: {e}")
            return False

    @staticmethod
    def clear_scan_cache():
        """Clear the network scan cache"""
        NetworkService._scan_cache = None
        NetworkService._last_scan_time = 0
        NetworkService._last_connection_change = time.time()

    @staticmethod
    def _cleanup_failed_connection(ssid: str):
        """
        Clean up failed connection attempts to allow retries.
        This is necessary because nmcli creates connection profiles even for failed attempts.
        """
        try:
            # Check if a connection with this SSID was created and delete it
            connections = nmcli.connection()
            for conn in connections:
                if conn.name == ssid:
                    try:
                        nmcli.connection.delete(ssid)
                        break
                    except:
                        # If we can't delete it, continue anyway
                        pass
        except:
            # If we can't clean up, continue anyway
            pass

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
                
                # Clear scan cache since we've modified network connections
                NetworkService.clear_scan_cache()
                    
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
        """
        Connect to a network with optimized performance
        
        Args:
            ssid: The SSID of the network to connect to
            password: Optional password for secured networks
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if password:
                # For secured networks with password
                nmcli.device.wifi_connect(ssid, password)
            elif NetworkService.is_wifi_known(ssid):
                # For known networks (saved passwords)
                NmcliExtensions.connect_to_open_or_saved_wifi(nmcli.device, ssid)
            else:
                # For open networks
                nmcli.device.wifi_connect(ssid)
            
            # Clear scan cache since we've modified network connections
            NetworkService.clear_scan_cache()
            
            return True, "Connected successfully"
            
        except nmcli._exception.ConnectionActivateFailedException as e:
            error_msg = str(e)
            if "Secrets were required, but not provided" in error_msg:
                return False, "Password required for this network"
            elif "No network with SSID" in error_msg:
                return False, f"Network '{ssid}' not found"
            else:
                # Clean up failed connection attempts to allow retries
                NetworkService._cleanup_failed_connection(ssid)
                return False, f"Connection failed: {error_msg}"
        except Exception as e:
            # Clean up failed connection attempts for any other errors as well
            if password:
                NetworkService._cleanup_failed_connection(ssid)
            return False, f"Connection error: {str(e)}"

    @staticmethod
    def disconnect_network(ssid:str) -> Tuple[bool, str]: 
        """Disconnect to a network using improved disconnection method"""
        try:
            nmcli.connection.down(ssid)
            # Clear scan cache since we've modified network connections
            NetworkService.clear_scan_cache()
            return True, "Disconnected Successfully"
        except Exception as e:
            return False, f"Connection error: {str(e)}"


    @staticmethod
    def get_connected_network() -> Optional[NetworkInfo]:
        """Get the currently connected network, if any"""
        try:
            # First check cached results
            cached_networks = NetworkService.scan_networks(force_rescan=False)
            for network in cached_networks:
                if network.is_connected:
                    return network
            
            # If not found in cache, scan for connected networks
            for wifi in nmcli.device.wifi():
                if getattr(wifi, 'in_use', False):
                    return NetworkInfo.from_wifi_device(wifi)
            
            return None
        except Exception as e:
            print(f"Error getting connected network: {e}")
            return None

    @staticmethod
    def get_wifi_details(ssid: str) -> Optional[NetworkInfo]:
        """Get detailed information for a specific wifi network"""
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

