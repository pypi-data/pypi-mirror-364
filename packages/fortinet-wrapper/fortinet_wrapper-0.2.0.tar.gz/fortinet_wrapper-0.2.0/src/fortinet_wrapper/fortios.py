"""Module Name: fortios.py

Project Name: fortinet_wrapper

Description:
    Represents an instance of a FortiOS device.

Usage:
    This module can be imported to create an instance of this class:
        from fortinet_wrapper.fortios import FortiOS

Author: HBNet Networks
"""

from enum import Enum, auto

import requests

# === Enums start here ===

class FortiOSVersion(Enum):
    """FortiOS version"""

    FORTIOS_7_2 = '7.2'
    FORTIOS_7_4 = '7.4'

class APIURL(Enum):
    """API URL for FortiOS"""

    GLOBAL = 'api/v2/cmdb/system/global'
    INTERFACE = 'api/v2/cmdb/system/interface'
    MANAGED_SWITCHES = 'api/v2/cmdb/switch-controller/managed-switch'
    MANAGED_APS = 'api/v2/cmdb/wireless-controller/wtp'
    FIRMWARE = 'api/v2/monitor/system/firmware'

class ManagedDeviceType(Enum):
    """Type of managed device"""

    INTERFACE = auto()
    FORTIAP = auto()
    FORTISWITCH = auto()

# === Enums end here ===

class FortiOS():
    """FortiOS device class

    !!!DOES NOT CURRENTLY SUPPORT VDOMs!!!
    This class represents a single Fortigate device and is used to perform all
    API functions.
    For initialization the base URL, API Key and FortiOS version is required.
    """

    # Private variables
    _base_address: str
    _api_key: str
    _verify_ssl: bool
    _version: FortiOSVersion
    _platform: str
    _firmware: str
    _system_global: dict
    _hostname: str
    _serial: str
    _base_headers = {
        'Accept' : 'application/json',
        'Authorization' : str()
        }

    # Device structures
    _interfaces: list
    _managed_switches: list
    _managed_aps: list

    # === Public properties start here ===

    @property
    def base_address(self) -> str:
        """Base URL of the device API"""
        return self._base_address

    @property
    def api_key(self) -> str:
        """API Key for authentication"""
        return self._api_key

    @property
    def verify_ssl(self) -> bool:
        """SSL Verification"""
        return self._verify_ssl

    @property
    def version(self) -> FortiOSVersion:
        """FortiOS version"""
        return self._version

    @property
    def hostname(self) -> str:
        """Hostname of the device"""
        return self._hostname

    @property
    def serial(self) -> str:
        """Device serial number"""
        return self._serial

    @property
    def system_global(self) -> dict:
        """System global configuration"""
        return self._system_global

    @property
    def platform(self) -> str:
        """Device hardware platform"""
        return self._platform

    @property
    def firmware(self) -> str:
        """Device firmware version"""
        return self._firmware

    @property
    def interfaces(self) -> list:
        """Device interfaces"""
        return self._interfaces

    @property
    def managed_switches(self) -> list:
        """Switches managed by this device"""
        return self._interfaces

    @property
    def managed_aps(self) -> list:
        """WAPs managed by this device"""
        return self._managed_aps

    # === Public properties end here ===

    # === Private methods start here ===

    def __init__(
            self, base_address: str,
            api_key: str,
            *,
            port: int = 443,
            verify_ssl: bool = True):
        """
        Initializes a Fortigate device and retrieves key configuration data.

        **PLEASE NOTE:**
        - Connections are required to be HTTPS
        - VDOMs are *not currently supported*

        The following configuration is retrieved:
        - System Global configuration
        - Interfaces
        - Managed Switches
        - Managed APs

        Args:
            base_address (str): Base URL of the device API.
            api_key (str): API key for authentication.
            version (FortiOSVersion): FortiOS version.
            port (int, optional): TCP port number. Defaults to 443.
            verify_ssl (bool, optional): Verify SSL certificates? Defaults to True.

        Raises:
            ValueError: If required parameters are not specified.
            ConnectionError: If the device cannot be reached for whatever reason.

        Returns:
            bool: True if initialized correctly.
        """
        # Confirm required parameters are specified
        if not base_address:
            raise ValueError('Base URL is required')
        if not api_key:
            raise ValueError('API Key is required')
        if not port:
            raise ValueError('Port is required')

        self._base_address = f'https://{base_address}:{str(port)}' # Assemble URL

        # self._base_address = base_address
        self._api_key = api_key
        self._verify_ssl = verify_ssl

        self._base_headers = self._base_headers.copy()  # Copy base headers
        self._base_headers['Authorization'] = f'Bearer {self._api_key}'

        # Test reachability
        self._check_reachable()

        self._get_system()
        self._interfaces = self.managed_device(ManagedDeviceType.INTERFACE)
        self._managed_switches = self.managed_device(ManagedDeviceType.FORTISWITCH)
        self._managed_aps = self.managed_device(ManagedDeviceType.FORTIAP)

        return True

    def _do_get(self, url: str, params: dict | None = None) -> dict:
        """Perform a GET request to device API

        Args:
            url (str, required): API URL.
            params (dict, optional): Additional query parameters.

        Raises:
            ValueError if required parameters are not specified.

        Returns:
            dict: JSON with response from the API call

        """
        if params is None: # If no params specified, use empty dict
            params = {}

        _request = requests.get(
            f'{self._base_address}/{url}',
            headers=self._base_headers,
            params=params,
            verify=self._verify_ssl, timeout=10
            )
        if _request.status_code == 200:
            return _request.json()
        elif _request.status_code == 401:
            raise ConnectionError(
                f'GET request to {url} failed with status \
                code {_request.status_code}: {_request.text}'
            )
        else:
            raise ValueError(
                f'GET request to {url} failed with status \
                code {_request.status_code}: {_request.text}')

    def _get_system(self):
        """Get basic system information

        Gets the system global configuration and stores it locally
        """
        _firmware_results: dict
        try:
            self._system_global = self._do_get(APIURL.GLOBAL.value) # Get system global
            _firmware_results = self._do_get(APIURL.FIRMWARE.value) # Get firmware
        except ValueError as e:
            raise ValueError(f'Failed to get system global configuration: {e}') from e

        self._hostname = self._system_global['results']['hostname']
        self._version = self._system_global['version']
        self._serial = self._system_global['serial']
        self._firmware = _firmware_results['results']['current']['version']
        self._platform = _firmware_results['results']['current']['platform-id']

    def _check_reachable(self) -> bool:
        """Check whether thid device is in fact reachable."""
        _reachable: bool
        _check_results: dict

        try:
            _check_results = self._do_get(APIURL.FIRMWARE.value)
        except ValueError as e:
            raise e
        except ConnectionError as e:
            raise e

        # Do a test connection and retrieve firmware version


        return True # TODO: Remove when logic is implemented.

    # === Private methods end here ===

    # === Public methods start here ===

    def managed_device(self,type: ManagedDeviceType, name: str = '') -> list:
        """
        Gets managed device information for the specified device type.

        Args:
            type (ManagedDeviceType): Type of managed device to retrieve.
                Must be one of the supported enum values.
            name (str, optional): Name of the managed device. Defaults to ''.
                An empty string returns all devices of the specified type.

        Returns:
            dict: A summary of managed device information.
        """
        _base_address: str = ''
        _url: str = ''

        _result_list = []
        _results: dict

        if not type:
            raise ValueError('Managed device type is required')

        match type:
            case ManagedDeviceType.INTERFACE:
                _base_address = APIURL.INTERFACE.value
            case ManagedDeviceType.FORTIAP:
                _base_address = APIURL.MANAGED_APS.value
            case ManagedDeviceType.FORTISWITCH:
                _base_address = APIURL.MANAGED_SWITCHES.value

        if name:  # If a name is specified, get that device
            _url = f'{_base_address}/{name}'
        else:  # Get all devices of that type
            _url = _base_address

        try:
            _results = self._do_get(_url)
        except ValueError as e:
            raise ValueError(f'Failed to get managed device: {e}') from e

        # Parse the results and assemble a summary list of switches
        for item in _results['results']:
            _result_list.append(item)

        return _result_list


    # === Public methods end here ===
