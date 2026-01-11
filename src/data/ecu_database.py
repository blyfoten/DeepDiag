"""
ECU database for managing multiple ECU connections and information.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class ECUInfo:
    """Information about an ECU."""
    can_id: int
    name: str
    description: str = ''
    protocol: str = ''
    supported_pids: List[int] = field(default_factory=list)
    properties: Dict[str, any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.name} (ID: 0x{self.can_id:03X})"


class ECUDatabase:
    """Database of ECUs found on the vehicle network."""

    # Common ECU names by CAN ID
    COMMON_ECUS = {
        0x7E8: 'Engine Control Module (ECM)',
        0x7E9: 'Transmission Control Module (TCM)',
        0x7EA: 'Anti-lock Braking System (ABS)',
        0x7EB: 'Body Control Module (BCM)',
        0x7EC: 'Instrument Cluster',
        0x7ED: 'Airbag Control Module',
        0x7EE: 'HVAC Control Module',
        0x7EF: 'Gateway Module',
    }

    def __init__(self):
        """Initialize ECU database."""
        self.ecus: Dict[int, ECUInfo] = {}

    def add_ecu(self, can_id: int, name: str = None, description: str = ''):
        """
        Add an ECU to the database.

        Args:
            can_id: CAN ID of the ECU
            name: ECU name (auto-detected if not provided)
            description: Additional description
        """
        if name is None:
            name = self.COMMON_ECUS.get(can_id, f'ECU 0x{can_id:03X}')

        ecu = ECUInfo(
            can_id=can_id,
            name=name,
            description=description
        )

        self.ecus[can_id] = ecu

    def remove_ecu(self, can_id: int):
        """
        Remove ECU from database.

        Args:
            can_id: CAN ID of the ECU
        """
        if can_id in self.ecus:
            del self.ecus[can_id]

    def get_ecu(self, can_id: int) -> Optional[ECUInfo]:
        """
        Get ECU information.

        Args:
            can_id: CAN ID of the ECU

        Returns:
            ECU info or None if not found.
        """
        return self.ecus.get(can_id)

    def get_all_ecus(self) -> List[ECUInfo]:
        """
        Get all ECUs in database.

        Returns:
            List of ECU info objects.
        """
        return list(self.ecus.values())

    def update_supported_pids(self, can_id: int, pids: List[int]):
        """
        Update list of supported PIDs for an ECU.

        Args:
            can_id: CAN ID of the ECU
            pids: List of supported PID numbers
        """
        ecu = self.get_ecu(can_id)
        if ecu:
            ecu.supported_pids = pids

    def set_property(self, can_id: int, key: str, value: any):
        """
        Set a property for an ECU.

        Args:
            can_id: CAN ID of the ECU
            key: Property key
            value: Property value
        """
        ecu = self.get_ecu(can_id)
        if ecu:
            ecu.properties[key] = value

    def get_property(self, can_id: int, key: str, default=None) -> any:
        """
        Get a property from an ECU.

        Args:
            can_id: CAN ID of the ECU
            key: Property key
            default: Default value if not found

        Returns:
            Property value or default.
        """
        ecu = self.get_ecu(can_id)
        if ecu:
            return ecu.properties.get(key, default)
        return default

    def clear(self):
        """Clear all ECUs from database."""
        self.ecus.clear()

    def get_ecu_count(self) -> int:
        """Get number of ECUs in database."""
        return len(self.ecus)
