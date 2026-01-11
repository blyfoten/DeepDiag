"""
CAN protocol operations and raw CAN frame handling.
"""

from typing import List, Optional, Tuple
from communication.elm327_connection import ELM327Connection
from communication.exceptions import InvalidResponseError


class CANFrame:
    """Represents a single CAN frame."""

    def __init__(self, can_id: int, data: List[int], extended: bool = False):
        """
        Initialize CAN frame.

        Args:
            can_id: CAN identifier
            data: Data bytes (up to 8 bytes)
            extended: True for 29-bit ID, False for 11-bit
        """
        self.can_id = can_id
        self.data = data
        self.extended = extended

    def __str__(self) -> str:
        """String representation of frame."""
        data_hex = ' '.join([f'{b:02X}' for b in self.data])
        id_str = f"{self.can_id:08X}" if self.extended else f"{self.can_id:03X}"
        return f"ID: {id_str}, Data: {data_hex}"


class CANProtocol:
    """CAN protocol handler for raw CAN operations."""

    def __init__(self, connection: ELM327Connection):
        """
        Initialize CAN protocol handler.

        Args:
            connection: Active ELM327 connection.
        """
        self.connection = connection

    def send_can_frame(self, can_id: int, data: List[int], extended: bool = False) -> bool:
        """
        Send a raw CAN frame.

        Args:
            can_id: CAN identifier
            data: Data bytes (up to 8 bytes)
            extended: Use 29-bit extended ID

        Returns:
            True if successful.
        """
        # Set CAN ID format if needed
        if extended:
            # Set to 29-bit mode
            self.connection.send_command('ATCP18')  # CAN Priority 18 (extended)
        else:
            # Set to 11-bit mode
            self.connection.send_command('ATCP00')  # Standard 11-bit

        # Format data bytes
        data_hex = ''.join([f'{b:02X}' for b in data])

        # Send frame
        if extended:
            cmd = f"{can_id:08X}{data_hex}"
        else:
            cmd = f"{can_id:03X}{data_hex}"

        response = self.connection.send_command(cmd)

        return 'OK' in response or response == ''

    def receive_can_frame(self, timeout: float = 1.0) -> Optional[CANFrame]:
        """
        Receive a single CAN frame.

        Args:
            timeout: Timeout in seconds

        Returns:
            CANFrame object or None if no frame received.
        """
        # Enable CAN monitoring mode
        response = self.connection.send_command('ATMA', delay=timeout)

        # Stop monitoring
        self.connection.send_command('')  # Send empty to stop

        if not response or 'NO DATA' in response:
            return None

        # Parse first frame from response
        frames = self._parse_can_frames(response)

        if frames:
            return frames[0]

        return None

    def monitor_can_bus(self, duration: float = 5.0) -> List[CANFrame]:
        """
        Monitor CAN bus for a duration.

        Args:
            duration: Duration in seconds

        Returns:
            List of captured CAN frames.
        """
        # Enable CAN monitoring mode
        response = self.connection.send_command('ATMA', delay=duration)

        # Stop monitoring
        self.connection.send_command('')

        if not response or 'NO DATA' in response:
            return []

        # Parse frames
        frames = self._parse_can_frames(response)

        return frames

    def set_can_filter(self, can_id: int, extended: bool = False) -> bool:
        """
        Set CAN receive filter to specific ID.

        Args:
            can_id: CAN ID to filter
            extended: True for 29-bit ID

        Returns:
            True if successful.
        """
        if extended:
            cmd = f'ATCF{can_id:08X}'
        else:
            cmd = f'ATCF{can_id:03X}'

        response = self.connection.send_command(cmd)
        return 'OK' in response

    def set_can_mask(self, mask: int, extended: bool = False) -> bool:
        """
        Set CAN receive mask.

        Args:
            mask: Mask value
            extended: True for 29-bit mask

        Returns:
            True if successful.
        """
        if extended:
            cmd = f'ATCM{mask:08X}'
        else:
            cmd = f'ATCM{mask:03X}'

        response = self.connection.send_command(cmd)
        return 'OK' in response

    def clear_can_filter(self) -> bool:
        """
        Clear CAN filter (receive all frames).

        Returns:
            True if successful.
        """
        # Set filter and mask to 0 to receive all
        self.set_can_filter(0)
        self.set_can_mask(0)
        return True

    def send_uds_request(self, service: int, data: List[int], ecu_id: int = 0x7DF) -> str:
        """
        Send UDS (Unified Diagnostic Services) request.

        Args:
            service: UDS service ID (e.g., 0x22 for ReadDataByIdentifier)
            data: Additional data bytes
            ecu_id: ECU CAN ID (default 0x7DF for broadcast)

        Returns:
            Response string.
        """
        # Build UDS frame
        frame_data = [len(data) + 1, service] + data

        # Pad to 8 bytes
        while len(frame_data) < 8:
            frame_data.append(0x00)

        # Send frame
        self.send_can_frame(ecu_id, frame_data, extended=False)

        # Receive response
        # UDS response is typically on ID 0x7E8-0x7EF
        response = self.connection.send_command('', delay=0.5)

        return response

    def _parse_can_frames(self, response: str) -> List[CANFrame]:
        """
        Parse CAN frames from monitoring response.

        Args:
            response: Raw response from ATMA command

        Returns:
            List of parsed CAN frames.
        """
        frames = []
        lines = response.split('\n')

        for line in lines:
            line = line.strip()

            if not line or line == 'SEARCHING...' or line == 'STOPPED':
                continue

            try:
                # Remove spaces
                line = line.replace(' ', '').upper()

                # Check for extended or standard ID
                # Standard: 3 hex digits (11-bit)
                # Extended: 8 hex digits (29-bit)

                if len(line) >= 11:  # Minimum: 3-digit ID + 8-digit data (4 bytes)
                    # Try to parse as standard frame
                    can_id = int(line[0:3], 16)
                    data_hex = line[3:]
                    extended = False
                elif len(line) >= 16:  # Extended: 8-digit ID + data
                    can_id = int(line[0:8], 16)
                    data_hex = line[8:]
                    extended = True
                else:
                    continue

                # Parse data bytes
                data = []
                for i in range(0, len(data_hex), 2):
                    if i + 1 < len(data_hex):
                        byte_val = int(data_hex[i:i+2], 16)
                        data.append(byte_val)

                if data:
                    frame = CANFrame(can_id, data, extended)
                    frames.append(frame)

            except ValueError:
                # Skip invalid frames
                continue

        return frames

    def detect_ecus(self) -> List[int]:
        """
        Detect available ECUs on CAN bus using functional addressing.

        Returns:
            List of ECU CAN IDs.
        """
        ecus = []

        # Common ECU addresses (response IDs)
        common_ecu_ids = [0x7E8, 0x7E9, 0x7EA, 0x7EB, 0x7EC, 0x7ED, 0x7EE, 0x7EF]

        # Send broadcast request (UDS service 0x3E - Tester Present)
        self.send_can_frame(0x7DF, [0x02, 0x3E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

        # Monitor for responses
        frames = self.monitor_can_bus(duration=2.0)

        # Extract unique ECU IDs from responses
        for frame in frames:
            if frame.can_id in common_ecu_ids and frame.can_id not in ecus:
                ecus.append(frame.can_id)

        return ecus
