"""
Module Name: config.py
Project Name: fortinet-wrapper

Description:
    Loads and stores the config for this project.

Usage:
    This module can be imported to access configuration variables
        or utility functions:
        import config

Author: HBNet Networks
"""

import os

from dotenv import load_dotenv


def load_env() -> dict:
    """
    Load environment variables from .env file.
    """
    load_dotenv()  # Load environment variables from .env file

    ENVIRONMENT = os.getenv('APP_ENV', 'dev')
    DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'
    ADDRESS = os.getenv('ADDRESS',None)
    API_KEY = os.getenv("API_KEY", None)
    VERIFY_SSL = os.getenv('VERIFY_SSL', 'true').lower() == 'true'
    PORT = os.getenv("PORT", None)

    # Additional config logic if needed
    if ENVIRONMENT == 'prod' and not API_KEY:
        raise ValueError('API_KEY must be set in prod')
    if not ADDRESS:
        raise ValueError('ADDRESS must be set')
    if not API_KEY:
        raise ValueError('API_KEY must be set')
    if not isinstance(DEBUG, bool):
        raise ValueError('DEBUG must be a boolean value')

    return {
        'ENVIRONMENT': ENVIRONMENT,
        'DEBUG': DEBUG,
        'ADDRESS': ADDRESS,
        'API_KEY': API_KEY,
        'VERIFY_SSL': VERIFY_SSL,
        'PORT' : PORT
    }
