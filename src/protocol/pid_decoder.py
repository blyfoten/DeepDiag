"""
PID value decoder for OBD-II responses.
"""

from typing import List, Any, Optional, Tuple
from data.pid_definitions import STANDARD_PIDS, PIDDefinition


class PIDDecoder:
    """Decoder for OBD-II PID values."""

    def __init__(self):
        """Initialize PID decoder."""
        self.custom_pids = {}

    def decode_response(self, mode: int, pid: int, data_bytes: List[int]) -> Any:
        """
        Decode PID response data.

        Args:
            mode: OBD mode number
            pid: PID number
            data_bytes: Raw data bytes from response

        Returns:
            Decoded value.
        """
        # Check custom PIDs first
        key = (mode, pid)
        if key in self.custom_pids:
            pid_def = self.custom_pids[key]
            return pid_def.decoder(data_bytes)

        # Check standard PIDs (Mode 01)
        if mode == 1 and pid in STANDARD_PIDS:
            pid_def = STANDARD_PIDS[pid]
            return pid_def.decoder(data_bytes)

        # Unknown PID, return raw bytes as hex string
        return ' '.join([f'{b:02X}' for b in data_bytes])

    def get_pid_info(self, mode: int, pid: int) -> Optional[PIDDefinition]:
        """
        Get PID definition.

        Args:
            mode: OBD mode number
            pid: PID number

        Returns:
            PID definition or None if not found.
        """
        # Check custom PIDs
        key = (mode, pid)
        if key in self.custom_pids:
            return self.custom_pids[key]

        # Check standard PIDs
        if mode == 1 and pid in STANDARD_PIDS:
            return STANDARD_PIDS[pid]

        return None

    def register_custom_pid(self, mode: int, pid_def: PIDDefinition):
        """
        Register a custom PID definition.

        Args:
            mode: OBD mode number
            pid_def: PID definition
        """
        key = (mode, pid_def.pid)
        self.custom_pids[key] = pid_def

    def parse_response_bytes(self, response: str) -> Tuple[int, int, List[int]]:
        """
        Parse OBD response string into mode, PID, and data bytes.

        Args:
            response: Response string (e.g., "41 0C 1A F8" or "410C1AF8")

        Returns:
            Tuple of (mode, pid, data_bytes)

        Raises:
            ValueError: If response format is invalid.
        """
        # Remove spaces and convert to uppercase
        response = response.replace(' ', '').upper()

        # Remove common prefixes
        response = response.replace('>', '').strip()

        # Minimum length is 4 characters (mode response + PID)
        if len(response) < 4:
            raise ValueError(f"Response too short: {response}")

        # First byte is mode response (e.g., 41 for mode 01)
        mode_response = int(response[0:2], 16)
        mode = mode_response - 0x40  # Mode response is mode + 0x40

        # Second byte is PID
        pid = int(response[2:4], 16)

        # Remaining bytes are data
        data_bytes = []
        for i in range(4, len(response), 2):
            if i + 1 < len(response):
                byte_val = int(response[i:i+2], 16)
                data_bytes.append(byte_val)
            elif i < len(response):
                # Odd number of hex digits, pad with 0
                byte_val = int(response[i] + '0', 16)
                data_bytes.append(byte_val)

        return mode, pid, data_bytes

    def decode_response_string(self, response: str) -> Tuple[int, int, Any]:
        """
        Decode full OBD response string.

        Args:
            response: Response string from ELM327

        Returns:
            Tuple of (mode, pid, decoded_value)
        """
        mode, pid, data_bytes = self.parse_response_bytes(response)
        value = self.decode_response(mode, pid, data_bytes)
        return mode, pid, value

    def format_value(self, mode: int, pid: int, value: Any) -> str:
        """
        Format decoded value with unit.

        Args:
            mode: OBD mode
            pid: PID number
            value: Decoded value

        Returns:
            Formatted string with value and unit.
        """
        pid_def = self.get_pid_info(mode, pid)

        if pid_def is None:
            return str(value)

        if isinstance(value, float):
            return f"{value:.2f} {pid_def.unit}".strip()
        else:
            return f"{value} {pid_def.unit}".strip()
