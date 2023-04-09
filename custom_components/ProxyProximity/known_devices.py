"""Known device types and their Bluetooth characteristics."""
from __future__ import annotations

from typing import Dict

# Dictionary of device types and their default TX power values
DEVICE_TYPES: Dict[str, int] = {
    "iPhone": -12,
    "iPad": -12,
    "Apple Watch": -12,
    "Mac": -17,
}
