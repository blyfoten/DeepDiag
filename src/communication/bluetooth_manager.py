"""
Bluetooth device discovery and management for ELM327 adapters.
Uses pyserial for cross-platform compatibility.
"""

import serial
import serial.tools.list_ports
from typing import List, Dict, Optional
from .exceptions import DeviceNotFoundError


class BluetoothManager:
    """Manages Bluetooth device discovery and enumeration."""

    def __init__(self):
        """Initialize Bluetooth manager."""
        self.devices = []

    def scan_devices(self) -> List[Dict[str, str]]:
        """
        Scan for available serial/Bluetooth devices.

        Returns:
            List of device dictionaries with 'port', 'description', and 'hwid' keys.
        """
        self.devices = []
        ports = serial.tools.list_ports.comports()

        for port in ports:
            device_info = {
                'port': port.device,
                'description': port.description,
                'hwid': port.hwid,
                'manufacturer': port.manufacturer or 'Unknown',
                'product': port.product or 'Unknown'
            }
            self.devices.append(device_info)

        return self.devices

    def get_elm327_devices(self) -> List[Dict[str, str]]:
        """
        Filter devices to find likely ELM327 adapters.

        Returns:
            List of devices that may be ELM327 adapters.
        """
        if not self.devices:
            self.scan_devices()

        # Common ELM327 identifiers in device description
        elm_keywords = ['elm327', 'obd', 'obdii', 'obd-ii', 'bluetooth', 'hc-05', 'hc-06']

        filtered_devices = []
        for device in self.devices:
            desc_lower = device['description'].lower()
            if any(keyword in desc_lower for keyword in elm_keywords):
                filtered_devices.append(device)

        # If no matches, return all devices (user may need to manually select)
        if not filtered_devices:
            return self.devices

        return filtered_devices

    def find_device_by_port(self, port_name: str) -> Optional[Dict[str, str]]:
        """
        Find device information by port name.

        Args:
            port_name: Serial port name (e.g., 'COM3', '/dev/rfcomm0')

        Returns:
            Device info dictionary or None if not found.
        """
        if not self.devices:
            self.scan_devices()

        for device in self.devices:
            if device['port'] == port_name:
                return device

        return None

    def get_bluetooth_port_pairs(self) -> List[tuple]:
        """
        Identify Bluetooth port pairs (outgoing/incoming).

        Returns:
            List of tuples: [(outgoing_port, incoming_port), ...]
        """
        if not self.devices:
            self.scan_devices()

        # Group Bluetooth ports by description
        bluetooth_ports = {}
        for device in self.devices:
            desc = device['description'].lower()
            if 'bluetooth' in desc or 'bth' in desc:
                base_desc = device['description']
                if base_desc not in bluetooth_ports:
                    bluetooth_ports[base_desc] = []
                bluetooth_ports[base_desc].append(device['port'])

        # Find pairs (usually sequential COM ports)
        pairs = []
        for ports in bluetooth_ports.values():
            if len(ports) == 2:
                # Lower number is typically outgoing
                ports.sort()
                pairs.append((ports[0], ports[1]))

        return pairs

    def is_likely_outgoing_port(self, port_name: str) -> Optional[bool]:
        """
        Determine if a port is likely the outgoing Bluetooth port.

        Args:
            port_name: Port name to check

        Returns:
            True if likely outgoing, False if likely incoming, None if unknown
        """
        pairs = self.get_bluetooth_port_pairs()

        for outgoing, incoming in pairs:
            if port_name == outgoing:
                return True
            elif port_name == incoming:
                return False

        return None
