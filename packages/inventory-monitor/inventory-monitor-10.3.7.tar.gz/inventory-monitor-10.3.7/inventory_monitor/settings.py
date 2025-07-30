"""
Plugin Settings Helper Module for Inventory Monitor Plugin.

This module provides centralized access to plugin configuration settings
and helper functions for commonly used settings.
"""

from django.conf import settings


def get_plugin_settings():
    """
    Get all plugin configuration settings.

    Returns:
        dict: Plugin configuration settings dictionary
    """
    return settings.PLUGINS_CONFIG.get("inventory_monitor", {})


def get_probe_recent_days():
    """
    Get the number of days to consider a probe "recent".

    Returns:
        int: Number of days (default: 7)
    """
    return get_plugin_settings().get("probe_recent_days", 7)


# Convenience constants using the settings functions
PLUGIN_SETTINGS = get_plugin_settings()
