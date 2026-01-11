"""
ELM327 AT command interface and device initialization.
"""

from typing import Optional, List
from communication.elm327_connection import ELM327Connection
from communication.exceptions import ProtocolError, InvalidResponseError


class ELM327:
    """ELM327 command interface for AT commands and device control."""

    # Supported protocols
    PROTOCOLS = {
        '0': 'Automatic',
        '1': 'SAE J1850 PWM (41.6 kbaud)',
        '2': 'SAE J1850 VPW (10.4 kbaud)',
        '3': 'ISO 9141-2 (5 baud init)',
        '4': 'ISO 14230-4 KWP (5 baud init)',
        '5': 'ISO 14230-4 KWP (fast init)',
        '6': 'ISO 15765-4 CAN (11 bit ID, 500 kbaud)',
        '7': 'ISO 15765-4 CAN (29 bit ID, 500 kbaud)',
        '8': 'ISO 15765-4 CAN (11 bit ID, 250 kbaud)',
        '9': 'ISO 15765-4 CAN (29 bit ID, 250 kbaud)',
        'A': 'SAE J1939 CAN (29 bit ID, 250 kbaud)',
        'B': 'User1 CAN (11 bit ID, 125 kbaud)',
        'C': 'User2 CAN (11 bit ID, 50 kbaud)'
    }

    def __init__(self, connection: ELM327Connection):
        """
        Initialize ELM327 protocol handler.

        Args:
            connection: Active ELM327 connection.
        """
        self.connection = connection
        self.version: Optional[str] = None
        self.protocol: Optional[str] = None
        self.voltage: Optional[float] = None

    def initialize(self, protocol: str = '0', echo: bool = False,
                   headers: bool = False, spaces: bool = True) -> bool:
        """
        Initialize ELM327 adapter with standard settings.

        Args:
            protocol: Protocol to use ('0' for automatic)
            echo: Enable command echo
            headers: Show headers in responses
            spaces: Add spaces between bytes

        Returns:
            True if initialization successful.

        Raises:
            ProtocolError: If initialization fails.
        """
        try:
            # Reset adapter
            response = self.reset()
            if 'ELM327' not in response:
                raise ProtocolError(f"Invalid reset response: {response}")

            # Store version
            self.version = response

            # Turn off echo
            self.set_echo(echo)

            # Set protocol
            self.set_protocol(protocol)

            # Configure headers
            self.set_headers(headers)

            # Configure spaces
            self.set_spaces(spaces)

            # Read voltage to test communication
            self.voltage = self.get_voltage()

            # Get current protocol
            self.protocol = self.describe_protocol()

            return True

        except Exception as e:
            raise ProtocolError(f"Initialization failed: {str(e)}")

    def reset(self) -> str:
        """
        Reset ELM327 adapter (ATZ command).

        Returns:
            Device identification string.
        """
        response = self.connection.send_command('ATZ', delay=1.5)
        return response

    def get_version(self) -> str:
        """
        Get ELM327 version (ATI or AT@1 command).

        Returns:
            Version string.
        """
        response = self.connection.send_command('ATI')
        self.version = response
        return response

    def set_echo(self, enabled: bool) -> bool:
        """
        Enable or disable command echo.

        Args:
            enabled: True to enable echo, False to disable.

        Returns:
            True if successful.
        """
        cmd = 'ATE1' if enabled else 'ATE0'
        response = self.connection.send_command(cmd)
        return 'OK' in response

    def set_protocol(self, protocol: str) -> bool:
        """
        Set OBD protocol.

        Args:
            protocol: Protocol number (0-C, see PROTOCOLS dict)

        Returns:
            True if successful.
        """
        cmd = f'ATSP{protocol}'
        response = self.connection.send_command(cmd)
        return 'OK' in response

    def set_auto_protocol(self) -> bool:
        """
        Enable automatic protocol detection.

        Returns:
            True if successful.
        """
        return self.set_protocol('0')

    def describe_protocol(self) -> str:
        """
        Get current protocol description.

        Returns:
            Protocol description string.
        """
        response = self.connection.send_command('ATDP')
        return response

    def describe_protocol_number(self) -> str:
        """
        Get current protocol number.

        Returns:
            Protocol number.
        """
        response = self.connection.send_command('ATDPN')
        return response

    def set_headers(self, enabled: bool) -> bool:
        """
        Enable or disable headers in responses.

        Args:
            enabled: True to show headers, False to hide.

        Returns:
            True if successful.
        """
        cmd = 'ATH1' if enabled else 'ATH0'
        response = self.connection.send_command(cmd)
        return 'OK' in response

    def set_spaces(self, enabled: bool) -> bool:
        """
        Enable or disable spaces between bytes.

        Args:
            enabled: True to add spaces, False to remove.

        Returns:
            True if successful.
        """
        cmd = 'ATS1' if enabled else 'ATS0'
        response = self.connection.send_command(cmd)
        return 'OK' in response

    def get_voltage(self) -> float:
        """
        Read vehicle voltage.

        Returns:
            Voltage in volts.
        """
        response = self.connection.send_command('ATRV')
        try:
            # Response format: "12.5V"
            voltage_str = response.replace('V', '').strip()
            voltage = float(voltage_str)
            self.voltage = voltage
            return voltage
        except ValueError:
            raise InvalidResponseError(f"Invalid voltage response: {response}")

    def set_timeout(self, timeout_ms: int) -> bool:
        """
        Set timeout for OBD responses.

        Args:
            timeout_ms: Timeout in milliseconds (multiples of 4ms, max 1020ms)

        Returns:
            True if successful.
        """
        # Convert to hex value (timeout / 4ms)
        timeout_val = min(255, timeout_ms // 4)
        cmd = f'ATST{timeout_val:02X}'
        response = self.connection.send_command(cmd)
        return 'OK' in response

    def set_adaptive_timing(self, mode: int) -> bool:
        """
        Set adaptive timing mode.

        Args:
            mode: 0=off, 1=auto1, 2=auto2

        Returns:
            True if successful.
        """
        cmd = f'ATAT{mode}'
        response = self.connection.send_command(cmd)
        return 'OK' in response

    def close_protocol(self) -> bool:
        """
        Close current protocol connection.

        Returns:
            True if successful.
        """
        response = self.connection.send_command('ATPC')
        return 'OK' in response

    def warm_start(self) -> str:
        """
        Warm start (ATWS command) - resets without changing settings.

        Returns:
            Device response.
        """
        response = self.connection.send_command('ATWS', delay=1.0)
        return response

    def set_can_filter(self, filter_id: int) -> bool:
        """
        Set CAN receive filter.

        Args:
            filter_id: CAN ID to filter (0-7FF for 11-bit, 0-1FFFFFFF for 29-bit)

        Returns:
            True if successful.
        """
        cmd = f'ATCF{filter_id:03X}'
        response = self.connection.send_command(cmd)
        return 'OK' in response

    def set_can_mask(self, mask: int) -> bool:
        """
        Set CAN receive mask.

        Args:
            mask: CAN mask value

        Returns:
            True if successful.
        """
        cmd = f'ATCM{mask:03X}'
        response = self.connection.send_command(cmd)
        return 'OK' in response

    def get_supported_pids(self, mode: str = '01') -> List[int]:
        """
        Get list of supported PIDs for a mode.

        Args:
            mode: OBD mode (default '01')

        Returns:
            List of supported PID numbers.
        """
        supported = []

        # PIDs 00, 20, 40, 60, 80, A0, C0, E0 return bitmaps of supported PIDs
        for base_pid in [0x00, 0x20, 0x40, 0x60, 0x80, 0xA0, 0xC0, 0xE0]:
            cmd = f'{mode}{base_pid:02X}'
            try:
                response = self.connection.send_command(cmd)

                # Parse response
                # Format: "41 00 BE 1F A8 13" (mode+PID followed by 4 data bytes)
                parts = response.replace(mode, '').replace(f'{base_pid:02X}', '').strip().split()

                if len(parts) >= 4:
                    # Each byte represents 8 PIDs
                    for byte_idx, byte_str in enumerate(parts[:4]):
                        try:
                            byte_val = int(byte_str, 16)
                            for bit in range(8):
                                if byte_val & (1 << (7 - bit)):
                                    pid_num = base_pid + (byte_idx * 8) + bit + 1
                                    if pid_num <= 0xFF:
                                        supported.append(pid_num)
                        except ValueError:
                            continue

            except Exception:
                # If query fails, stop checking
                break

        return supported

    def send_raw_command(self, command: str, delay: float = 0.1) -> str:
        """
        Send raw command to adapter.

        Args:
            command: Raw command string
            delay: Delay after sending

        Returns:
            Response from adapter.
        """
        return self.connection.send_command(command, delay=delay)
