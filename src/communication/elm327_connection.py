"""
ELM327 connection management with automatic reconnection and error handling.
"""

import serial
import time
import threading
from typing import Optional, Callable
from communication.exceptions import ConnectionError, TimeoutError, InvalidResponseError


class ELM327Connection:
    """Manages serial connection to ELM327 adapter."""

    # Common ELM327 responses
    PROMPT = '>'
    OK = 'OK'
    ERROR = 'ERROR'
    NO_DATA = 'NO DATA'
    UNABLE_TO_CONNECT = 'UNABLE TO CONNECT'
    BUS_INIT = 'BUS INIT'
    SEARCHING = 'SEARCHING'

    def __init__(self, port: str, baudrate: int = 38400, timeout: float = 3.0):
        """
        Initialize ELM327 connection.

        Args:
            port: Serial port name (e.g., 'COM3', '/dev/rfcomm0')
            baudrate: Connection speed (default 38400, may be 9600, 115200, etc.)
            timeout: Read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial: Optional[serial.Serial] = None
        self.connected = False
        self.lock = threading.Lock()

        # Callbacks
        self.on_disconnect_callback: Optional[Callable] = None

    def connect(self) -> bool:
        """
        Connect to ELM327 device.

        Returns:
            True if connection successful, False otherwise.

        Raises:
            ConnectionError: If connection fails.
        """
        try:
            with self.lock:
                if self.connected:
                    return True

                self.serial = serial.Serial(
                    port=self.port,
                    baudrate=self.baudrate,
                    timeout=self.timeout,
                    write_timeout=self.timeout
                )

                # Flush buffers
                self.serial.reset_input_buffer()
                self.serial.reset_output_buffer()

                self.connected = True
                return True

        except serial.SerialException as e:
            raise ConnectionError(f"Failed to connect to {self.port}: {str(e)}")

    def disconnect(self):
        """Disconnect from ELM327 device."""
        with self.lock:
            if self.serial and self.serial.is_open:
                self.serial.close()
            self.connected = False

    def is_connected(self) -> bool:
        """Check if connection is active."""
        with self.lock:
            return self.connected and self.serial is not None and self.serial.is_open

    def send_command(self, command: str, delay: float = 0.1) -> str:
        """
        Send command to ELM327 and receive response.

        Args:
            command: Command string (without terminator)
            delay: Delay after sending command (seconds)

        Returns:
            Response string from adapter.

        Raises:
            ConnectionError: If not connected.
            TimeoutError: If response times out.
            InvalidResponseError: If response is invalid.
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to device")

        with self.lock:
            try:
                # Clear buffers
                self.serial.reset_input_buffer()

                # Send command with carriage return
                cmd_bytes = (command + '\r').encode('ascii')
                self.serial.write(cmd_bytes)

                # Wait for adapter to process
                time.sleep(delay)

                # Read response
                response = self._read_response()

                return response

            except serial.SerialException as e:
                self.connected = False
                if self.on_disconnect_callback:
                    self.on_disconnect_callback()
                raise ConnectionError(f"Communication error: {str(e)}")

    def _read_response(self, timeout: Optional[float] = None) -> str:
        """
        Read response from ELM327 until prompt character.

        Args:
            timeout: Override default timeout (seconds)

        Returns:
            Response string without prompt.

        Raises:
            TimeoutError: If no response within timeout.
        """
        if timeout is None:
            timeout = self.timeout

        response_lines = []
        start_time = time.time()

        while True:
            # Check timeout
            if time.time() - start_time > timeout:
                raise TimeoutError("Response timeout")

            # Read available data
            if self.serial.in_waiting > 0:
                try:
                    line = self.serial.readline().decode('ascii', errors='ignore').strip()

                    if line:
                        # Check for prompt (may be on same line or separate)
                        if self.PROMPT in line:
                            # Remove prompt and add remaining text
                            line = line.replace(self.PROMPT, '').strip()
                            if line:
                                response_lines.append(line)
                            break
                        else:
                            response_lines.append(line)

                except UnicodeDecodeError:
                    # Skip invalid characters
                    continue
            else:
                # Small delay to avoid busy waiting
                time.sleep(0.01)

        # Join lines and clean up
        response = '\n'.join(response_lines)

        # Remove echo if present (command might be echoed back)
        return response.strip()

    def send_command_raw(self, command: str) -> bytes:
        """
        Send command and return raw bytes response.

        Args:
            command: Command string

        Returns:
            Raw bytes from adapter.
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to device")

        with self.lock:
            self.serial.reset_input_buffer()
            self.serial.write((command + '\r').encode('ascii'))
            time.sleep(0.1)

            # Read until prompt
            response = b''
            start_time = time.time()

            while time.time() - start_time < self.timeout:
                if self.serial.in_waiting > 0:
                    data = self.serial.read(self.serial.in_waiting)
                    response += data
                    if b'>' in response:
                        break
                time.sleep(0.01)

            return response

    def set_disconnect_callback(self, callback: Callable):
        """
        Set callback to be called on disconnection.

        Args:
            callback: Function to call when disconnected.
        """
        self.on_disconnect_callback = callback

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
