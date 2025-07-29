"""
Module Name: testing.py
Project Name: conduit

Description:
    Used to test the Fortigate API wrapper.

Usage:
    This module can be imported to access configuration variables
        or utility functions:
        import env

Author: HBNet Networks
"""

import json

import config
import fortios

# Load environment variables
ENV:dict = config.load_env()

fgt = fortios.FortiOS(
    base_address=ENV['ADDRESS'],
    api_key=ENV['API_KEY'],
    verify_ssl=ENV['VERIFY_SSL'],
    port=ENV['PORT']
)

print(f"Global Config: {json.dumps(fgt.system_global, indent=2)}")

#print(interfaces)  # Example usage of the Fortigate API wrapper
# This is where you would call methods on the fgt object to interact with the Fortigate
# For example:  # fgt.get_firewall_policies()
# --- IGNORE ---
