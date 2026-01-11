"""
OBD-II protocol implementation for modes 01-09.
"""

from typing import List, Dict, Any, Optional, Tuple
from communication.elm327_connection import ELM327Connection
from communication.exceptions import InvalidResponseError, TimeoutError
from protocol.pid_decoder import PIDDecoder


class OBD2Protocol:
    """OBD-II protocol handler for standard modes."""

    # OBD-II modes
    MODE_CURRENT_DATA = '01'
    MODE_FREEZE_FRAME = '02'
    MODE_DTCS = '03'
    MODE_CLEAR_DTCS = '04'
    MODE_O2_MONITORING = '05'
    MODE_TEST_RESULTS = '06'
    MODE_PENDING_DTCS = '07'
    MODE_CONTROL = '08'
    MODE_VEHICLE_INFO = '09'

    def __init__(self, connection: ELM327Connection):
        """
        Initialize OBD-II protocol handler.

        Args:
            connection: Active ELM327 connection.
        """
        self.connection = connection
        self.decoder = PIDDecoder()

    def query_pid(self, mode: str, pid: int) -> Any:
        """
        Query a specific PID.

        Args:
            mode: OBD mode (e.g., '01')
            pid: PID number (0x00-0xFF)

        Returns:
            Decoded PID value.

        Raises:
            InvalidResponseError: If response is invalid.
            TimeoutError: If query times out.
        """
        # Format command
        cmd = f"{mode}{pid:02X}"

        # Send command
        response = self.connection.send_command(cmd)

        # Check for common error responses
        if not response or response in ['NO DATA', 'UNABLE TO CONNECT', 'ERROR']:
            raise InvalidResponseError(f"Invalid response: {response}")

        # Decode response
        try:
            _, _, value = self.decoder.decode_response_string(response)
            return value
        except Exception as e:
            raise InvalidResponseError(f"Failed to decode response '{response}': {str(e)}")

    def query_pid_raw(self, mode: str, pid: int) -> str:
        """
        Query PID and return raw response string.

        Args:
            mode: OBD mode
            pid: PID number

        Returns:
            Raw response string.
        """
        cmd = f"{mode}{pid:02X}"
        response = self.connection.send_command(cmd)
        return response

    def query_multiple_pids(self, mode: str, pids: List[int]) -> Dict[int, Any]:
        """
        Query multiple PIDs sequentially.

        Args:
            mode: OBD mode
            pids: List of PID numbers

        Returns:
            Dictionary mapping PID number to decoded value.
        """
        results = {}

        for pid in pids:
            try:
                value = self.query_pid(mode, pid)
                results[pid] = value
            except Exception:
                # Skip PIDs that fail
                continue

        return results

    def get_current_data(self, pid: int) -> Any:
        """
        Get current data (Mode 01).

        Args:
            pid: PID number

        Returns:
            Decoded value.
        """
        return self.query_pid(self.MODE_CURRENT_DATA, pid)

    def get_freeze_frame(self, pid: int, frame: int = 0) -> Any:
        """
        Get freeze frame data (Mode 02).

        Args:
            pid: PID number
            frame: Frame number (0-based)

        Returns:
            Decoded value.
        """
        # For freeze frame, need to specify frame number
        # Command format: 02 <frame> <PID>
        # Simplified: just query PID (ELM327 will use frame 0)
        return self.query_pid(self.MODE_FREEZE_FRAME, pid)

    def get_dtcs(self) -> List[str]:
        """
        Get stored diagnostic trouble codes (Mode 03).

        Returns:
            List of DTC strings.
        """
        response = self.connection.send_command(self.MODE_DTCS)

        if not response or 'NO DATA' in response:
            return []

        # Parse DTCs from response
        dtcs = self._parse_dtcs(response)
        return dtcs

    def clear_dtcs(self) -> bool:
        """
        Clear diagnostic trouble codes (Mode 04).

        Returns:
            True if successful.
        """
        response = self.connection.send_command(self.MODE_CLEAR_DTCS)
        return 'OK' in response or response == ''

    def get_pending_dtcs(self) -> List[str]:
        """
        Get pending diagnostic trouble codes (Mode 07).

        Returns:
            List of DTC strings.
        """
        response = self.connection.send_command(self.MODE_PENDING_DTCS)

        if not response or 'NO DATA' in response:
            return []

        dtcs = self._parse_dtcs(response)
        return dtcs

    def get_vehicle_info(self, pid: int) -> Any:
        """
        Get vehicle information (Mode 09).

        Args:
            pid: Info PID number

        Returns:
            Decoded information.
        """
        return self.query_pid(self.MODE_VEHICLE_INFO, pid)

    def get_vin(self) -> Optional[str]:
        """
        Get Vehicle Identification Number (Mode 09, PID 02).

        Returns:
            VIN string or None if not available.
        """
        try:
            # VIN is PID 02 in Mode 09
            response = self.query_pid_raw(self.MODE_VEHICLE_INFO, 0x02)

            # VIN response is multi-line, need to concatenate
            # Remove mode and PID bytes, extract ASCII
            vin_bytes = []

            lines = response.split('\n')
            for line in lines:
                # Remove spaces
                line = line.replace(' ', '').upper()

                # Skip mode/PID header
                if line.startswith('4902'):
                    line = line[4:]

                # Parse hex bytes and convert to ASCII
                for i in range(0, len(line), 2):
                    if i + 1 < len(line):
                        byte_val = int(line[i:i+2], 16)
                        if 32 <= byte_val <= 126:  # Printable ASCII
                            vin_bytes.append(chr(byte_val))

            vin = ''.join(vin_bytes).strip()

            if len(vin) == 17:  # Valid VIN length
                return vin

            return None

        except Exception:
            return None

    def _parse_dtcs(self, response: str) -> List[str]:
        """
        Parse DTC codes from Mode 03/07 response.

        Args:
            response: Raw response string

        Returns:
            List of DTC strings.
        """
        dtcs = []

        # Remove mode response prefix (43 or 47)
        response = response.replace('43', '').replace('47', '').strip()

        # Remove spaces
        response = response.replace(' ', '').upper()

        # DTCs are encoded as 2-byte pairs
        # First byte: first two characters
        # Second byte: last two characters
        for i in range(0, len(response), 4):
            if i + 3 < len(response):
                try:
                    byte1 = int(response[i:i+2], 16)
                    byte2 = int(response[i+2:i+4], 16)

                    # Skip if both bytes are 0 (padding)
                    if byte1 == 0 and byte2 == 0:
                        continue

                    # First 2 bits of byte1 determine letter
                    letter_map = {0: 'P', 1: 'C', 2: 'B', 3: 'U'}
                    letter = letter_map[(byte1 >> 6) & 0x03]

                    # Next 2 bits are first digit
                    digit1 = (byte1 >> 4) & 0x03

                    # Last 4 bits of byte1 are second digit
                    digit2 = byte1 & 0x0F

                    # Byte2 contains last two digits
                    digit3 = (byte2 >> 4) & 0x0F
                    digit4 = byte2 & 0x0F

                    dtc = f"{letter}{digit1}{digit2:X}{digit3:X}{digit4:X}"
                    dtcs.append(dtc)

                except ValueError:
                    continue

        return dtcs

    def get_supported_pids(self, mode: str = '01') -> List[int]:
        """
        Get list of supported PIDs for a mode.

        Args:
            mode: OBD mode (default '01')

        Returns:
            List of supported PID numbers.
        """
        supported = []

        # PIDs 00, 20, 40, 60, 80, A0, C0, E0 return bitmaps
        for base_pid in [0x00, 0x20, 0x40, 0x60, 0x80, 0xA0, 0xC0, 0xE0]:
            try:
                response = self.query_pid_raw(mode, base_pid)

                # Parse response to get bitmap
                _, _, data_bytes = self.decoder.parse_response_bytes(response)

                if len(data_bytes) >= 4:
                    # Each byte represents 8 PIDs
                    for byte_idx, byte_val in enumerate(data_bytes[:4]):
                        for bit in range(8):
                            if byte_val & (1 << (7 - bit)):
                                pid_num = base_pid + (byte_idx * 8) + bit + 1
                                if pid_num <= 0xFF:
                                    supported.append(pid_num)

            except Exception:
                # Stop on first failure
                break

        return supported
