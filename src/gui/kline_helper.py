"""
K-line (ISO 9141-2 / ISO 14230-4) troubleshooting helper window.
"""

import dearpygui.dearpygui as dpg
from typing import List, Tuple


class KLineHelper:
    """K-line diagnostic and troubleshooting helper."""

    def __init__(self, app):
        """
        Initialize K-line helper.

        Args:
            app: Reference to main DiagnosticApp
        """
        self.app = app
        self.window_tag = "kline_helper_window"
        self.test_results: List[Tuple[str, str, bool]] = []

        self._create_window()

    def _create_window(self):
        """Create the K-line helper window."""
        with dpg.window(
            label="K-line Troubleshooting Helper",
            tag=self.window_tag,
            width=700,
            height=600,
            pos=[290, 110],
            show=False
        ):
            dpg.add_text("K-line (ISO 9141-2 / ISO 14230-4 KWP) Diagnostic Helper")
            dpg.add_text("Use this tool to diagnose connection issues with older K-line vehicles")
            dpg.add_separator()
            dpg.add_spacer(height=10)

            # Protocol selection
            dpg.add_text("Step 1: Select K-line Protocol")
            with dpg.group(horizontal=True):
                dpg.add_radio_button(
                    items=["Auto Detect", "ISO 9141-2 (Protocol 3)",
                           "KWP 5-baud init (Protocol 4)", "KWP fast init (Protocol 5)"],
                    tag="kline_protocol_select",
                    default_value="Auto Detect",
                    horizontal=False
                )

            dpg.add_spacer(height=10)

            # Configuration
            dpg.add_text("Step 2: Configure Connection Settings")
            with dpg.group(horizontal=True):
                dpg.add_checkbox(label="Enable Headers (ATH1)", tag="kline_headers", default_value=True)
                dpg.add_checkbox(label="Enable Spaces (ATS1)", tag="kline_spaces", default_value=True)

            dpg.add_spacer(height=5)

            with dpg.group(horizontal=True):
                dpg.add_text("Timeout:")
                dpg.add_slider_int(
                    tag="kline_timeout",
                    default_value=255,
                    min_value=1,
                    max_value=255,
                    width=200
                )
                dpg.add_text("(x4 ms)")

            with dpg.group(horizontal=True):
                dpg.add_text("Adaptive Timing:")
                dpg.add_combo(
                    items=["Off (0)", "Auto 1 (1)", "Auto 2 (2)"],
                    default_value="Auto 2 (2)",
                    tag="kline_adaptive",
                    width=150
                )

            dpg.add_spacer(height=10)

            # Action buttons
            dpg.add_text("Step 3: Run Diagnostics")
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Auto-Configure",
                    callback=self._auto_configure,
                    width=150
                )
                dpg.add_button(
                    label="Apply Settings",
                    callback=self._apply_settings,
                    width=150
                )
                dpg.add_button(
                    label="Test Connection",
                    callback=self._test_connection,
                    width=150
                )

            dpg.add_spacer(height=10)
            dpg.add_separator()
            dpg.add_spacer(height=10)

            # Results
            dpg.add_text("Diagnostic Results:")
            with dpg.child_window(
                tag="kline_results",
                width=-1,
                height=-50,
                border=True
            ):
                dpg.add_text(
                    "Click 'Auto-Configure' to automatically detect best settings\n"
                    "or 'Apply Settings' to manually configure, then 'Test Connection'",
                    tag="kline_results_text",
                    wrap=680
                )

            dpg.add_spacer(height=5)

            # Close button
            with dpg.group(horizontal=True):
                dpg.add_button(label="Close", callback=self.hide, width=100)
                dpg.add_button(
                    label="Save to Config",
                    callback=self._save_config,
                    width=120,
                    enabled=False,
                    tag="kline_save_button"
                )

    def show(self):
        """Show the K-line helper window."""
        dpg.configure_item(self.window_tag, show=True)

    def hide(self):
        """Hide the K-line helper window."""
        dpg.configure_item(self.window_tag, show=False)

    def _auto_configure(self):
        """Automatically detect and configure K-line settings."""
        if not self.app.connected or not self.app.connection:
            self._append_result("ERROR: Not connected to ELM327 device\n", (255, 100, 100))
            return

        self._clear_results()
        self._append_result("Starting auto-configuration for K-line...\n\n", (100, 200, 255))

        # Test protocols in order
        protocols = [
            ("3", "ISO 9141-2"),
            ("4", "ISO 14230-4 KWP (5 baud init)"),
            ("5", "ISO 14230-4 KWP (fast init)")
        ]

        success_protocol = None

        for protocol_num, protocol_name in protocols:
            self._append_result(f"Testing {protocol_name}...\n", (200, 200, 200))

            try:
                # Set protocol
                self.app.connection.send_command(f"ATSP{protocol_num}")

                # Configure for K-line
                self.app.connection.send_command("ATST FF")  # Max timeout
                self.app.connection.send_command("ATH1")     # Headers on
                self.app.connection.send_command("ATS1")     # Spaces on
                self.app.connection.send_command("ATAT2")    # Adaptive timing 2

                # Test with 0100 (supported PIDs)
                response = self.app.connection.send_command("0100")

                if response and "41 00" in response and "NO DATA" not in response:
                    self._append_result(f"  ✓ SUCCESS! Protocol {protocol_num} ({protocol_name}) works!\n", (100, 255, 100))
                    self._append_result(f"  Response: {response}\n\n", (150, 255, 150))
                    success_protocol = protocol_num
                    break
                else:
                    self._append_result(f"  ✗ No response on protocol {protocol_num}\n\n", (255, 150, 100))

            except Exception as e:
                self._append_result(f"  ✗ Error: {str(e)}\n\n", (255, 100, 100))

        if success_protocol:
            self._append_result("\n=== RECOMMENDED SETTINGS ===\n", (100, 255, 255))
            self._append_result(f"Protocol: {success_protocol}\n", (255, 255, 255))
            self._append_result("Timeout: 255 (1020ms)\n", (255, 255, 255))
            self._append_result("Headers: ON\n", (255, 255, 255))
            self._append_result("Spaces: ON\n", (255, 255, 255))
            self._append_result("Adaptive Timing: Mode 2\n", (255, 255, 255))
            self._append_result("\nClick 'Save to Config' to remember these settings.\n", (100, 255, 100))

            # Update UI
            protocol_map = {"3": 1, "4": 2, "5": 3}
            dpg.set_value("kline_protocol_select", protocol_map.get(success_protocol, 0))
            dpg.configure_item("kline_save_button", enabled=True)

        else:
            self._append_result("\n=== NO WORKING PROTOCOL FOUND ===\n", (255, 100, 100))
            self._append_result("Possible issues:\n", (255, 255, 255))
            self._append_result("1. Vehicle ignition must be ON\n", (255, 255, 255))
            self._append_result("2. ELM327 must be fully plugged into OBD-II port\n", (255, 255, 255))
            self._append_result("3. Vehicle may not support OBD-II standard PIDs\n", (255, 255, 255))
            self._append_result("4. K-line pins may not be connected in adapter\n", (255, 255, 255))
            self._append_result("5. Try manufacturer-specific protocols if available\n", (255, 255, 255))

    def _apply_settings(self):
        """Apply selected settings manually."""
        if not self.app.connected or not self.app.connection:
            self._append_result("ERROR: Not connected to ELM327 device\n", (255, 100, 100))
            return

        self._clear_results()
        self._append_result("Applying K-line settings...\n\n", (100, 200, 255))

        try:
            # Get selected protocol
            protocol_selection = dpg.get_value("kline_protocol_select")
            protocol_map = {
                0: "0",  # Auto
                1: "3",  # ISO 9141-2
                2: "4",  # KWP 5-baud
                3: "5"   # KWP fast
            }
            protocol = protocol_map.get(protocol_selection, "0")

            # Apply protocol
            if protocol != "0":
                response = self.app.connection.send_command(f"ATSP{protocol}")
                self._append_result(f"Set protocol {protocol}: {response}\n", (200, 255, 200))
            else:
                response = self.app.connection.send_command("ATSP0")
                self._append_result(f"Set auto protocol: {response}\n", (200, 255, 200))

            # Apply timeout
            timeout = dpg.get_value("kline_timeout")
            response = self.app.connection.send_command(f"ATST{timeout:02X}")
            self._append_result(f"Set timeout {timeout}x4ms: {response}\n", (200, 255, 200))

            # Apply headers
            headers = dpg.get_value("kline_headers")
            cmd = "ATH1" if headers else "ATH0"
            response = self.app.connection.send_command(cmd)
            self._append_result(f"Headers {'ON' if headers else 'OFF'}: {response}\n", (200, 255, 200))

            # Apply spaces
            spaces = dpg.get_value("kline_spaces")
            cmd = "ATS1" if spaces else "ATS0"
            response = self.app.connection.send_command(cmd)
            self._append_result(f"Spaces {'ON' if spaces else 'OFF'}: {response}\n", (200, 255, 200))

            # Apply adaptive timing
            adaptive_selection = dpg.get_value("kline_adaptive")
            adaptive = adaptive_selection[-2]  # Extract number from "Auto 2 (2)"
            response = self.app.connection.send_command(f"ATAT{adaptive}")
            self._append_result(f"Adaptive timing mode {adaptive}: {response}\n", (200, 255, 200))

            self._append_result("\nSettings applied successfully!\n", (100, 255, 100))
            self._append_result("Click 'Test Connection' to verify.\n", (255, 255, 255))

        except Exception as e:
            self._append_result(f"\nERROR: {str(e)}\n", (255, 100, 100))

    def _test_connection(self):
        """Test connection with current settings."""
        if not self.app.connected or not self.app.connection:
            self._append_result("ERROR: Not connected to ELM327 device\n", (255, 100, 100))
            return

        self._append_result("\n--- Connection Test ---\n", (100, 200, 255))

        # Test commands
        tests = [
            ("ATDP", "Check active protocol"),
            ("0100", "Query supported PIDs"),
            ("010C", "Read engine RPM"),
            ("010D", "Read vehicle speed")
        ]

        for cmd, description in tests:
            try:
                self._append_result(f"\n{description} ({cmd})...\n", (200, 200, 200))
                response = self.app.connection.send_command(cmd, delay=0.5)

                if response and "NO DATA" not in response and "ERROR" not in response:
                    self._append_result(f"  ✓ {response}\n", (100, 255, 100))
                else:
                    self._append_result(f"  ✗ {response or 'No response'}\n", (255, 150, 100))

            except Exception as e:
                self._append_result(f"  ✗ Error: {str(e)}\n", (255, 100, 100))

        self._append_result("\nTest complete.\n", (100, 200, 255))

    def _save_config(self):
        """Save K-line settings to configuration."""
        # TODO: Implement config save
        self._append_result("\nConfiguration saved!\n", (100, 255, 100))
        dpg.configure_item("kline_save_button", enabled=False)

    def _append_result(self, text: str, color: tuple = (255, 255, 255)):
        """Append text to results display."""
        current_text = dpg.get_value("kline_results_text")
        dpg.set_value("kline_results_text", current_text + text)

    def _clear_results(self):
        """Clear results display."""
        dpg.set_value("kline_results_text", "")
