#!/usr/bin/env python3
"""
Version information for Cogzia Alpha v1.5

This file contains version information used for update checking and tracking.
"""

__version__ = "1.5.0"
__version_info__ = (1, 5, 0)
__release_date__ = "2025-07-22"
__update_channel__ = "stable"  # stable or alpha

def get_version_string():
    """Get the full version string."""
    return f"Cogzia Alpha v{__version__}"

def parse_version(version_str):
    """Parse a version string into a tuple for comparison."""
    try:
        # Handle versions like "1.5.0" or "v1.5.0"
        clean_version = version_str.lstrip('v')
        parts = clean_version.split('.')
        return tuple(int(p) for p in parts[:3])  # Major, minor, patch
    except:
        return (0, 0, 0)

def is_newer_version(remote_version, local_version=__version__):
    """Check if remote version is newer than local version."""
    remote_tuple = parse_version(remote_version)
    local_tuple = parse_version(local_version)
    return remote_tuple > local_tuple