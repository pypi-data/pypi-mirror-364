# Fortiner Wrapper

**Fortinet Wrapper** is a Python wrapper for the FortiOS API, designed to simplify automation and integration with Fortinet devices. It provides a clean, Pythonic interface to interact with FortiGate firewalls.

## Disclaimer

This project is an **independent, community-developed Python wrapper** for Fortinet APIs. It is **not affiliated with, maintained by, or endorsed by Fortinet, Inc.**

All product names, logos, and trademarks used in this project are the property of their respective owners. "Fortinet", "FortiGate", and other associated names are trademarks or registered trademarks of Fortinet, Inc., used here solely for descriptive and interoperability purposes under fair use.

## Please note
This project is a Work In Progress. Please check back regularly for updates.

## Features

- Access and retrieve FortiOS device config via API
- Designed for easy extension to support FortiSwitch, FortiAP and FortiManager in future releases
- Simplifies common network automation tasks
- Supports Python 3.10+

## Installation
Clone this GitHub Repo. In future release:

    pip install fortinet_wrapper

## Usage

Basic example:

    from fortiner_wrapper import fortios
    import json

    fgt = fortios.FortiOS(
        base_address='YOUR_DEVICE_ADDRESS',
        api_key='YOUR_API_KEY',
        verify_ssl=False,
        port=8443 # If non-standard https port
    )

    print(fgt.serial) # Serial number of the device
    print(fgt.hostname) # Hostname of the device
    print(fgt.version)  # FortiOS version of the device

    interfaces = fgt.interface() # Get all interfaces
    interfaces = fgt.interface(name='port1') # Get specific interface by name

## Roadmap

- Add configuration PUT methods
- Add FortiManager API support
- Add FortiSwitch API support
- Improved error handling and logging

## Contributing

Contributions and suggestions are welcome! Please open issues or pull requests.

## License

This project is licensed under the GNU/GPL License. See the [LICENSE](LICENSE) file for details.

---

© 2025 HBNet Networks
