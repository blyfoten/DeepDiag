"""
Connection window for device scanning and connection management.
"""

import dearpygui.dearpygui as dpg
from typing import List, Dict


class ConnectionWindow:
    """Connection management window."""

    def __init__(self, app):
        """
        Initialize connection window.

        Args:
            app: Reference to main DiagnosticApp
        """
        self.app = app
        self.window_tag = "connection_window"
        self.devices: List[Dict] = []
        self.selected_device = None

        self._create_window()

    def _create_window(self):
        """Create the connection window."""
        with dpg.window(
            label="Connection Manager",
            tag=self.window_tag,
            width=600,
            height=400,
            pos=[340, 160],
            show=False,
            modal=True
        ):
            dpg.add_text("Available Devices:")
            dpg.add_spacer(height=5)

            # Device list
            with dpg.group(tag="device_list_group"):
                dpg.add_text("Click 'Scan' to find devices")

            dpg.add_spacer(height=10)

            # Connection settings
            with dpg.group(horizontal=True):
                dpg.add_text("Baudrate:")
                dpg.add_combo(
                    items=["9600", "38400", "57600", "115200"],
                    default_value="38400",
                    tag="baudrate_combo",
                    width=100
                )

            dpg.add_spacer(height=10)

            # Buttons
            with dpg.group(horizontal=True):
                dpg.add_button(label="Scan", callback=self._scan_devices, width=100)
                dpg.add_button(
                    label="Connect",
                    callback=self._connect,
                    width=100,
                    tag="connect_button",
                    enabled=False
                )
                dpg.add_button(label="Cancel", callback=self.hide, width=100)

            dpg.add_spacer(height=10)

            # Status text
            dpg.add_text("", tag="connection_status_text")

    def show(self):
        """Show the connection window."""
        dpg.configure_item(self.window_tag, show=True)
        # Auto-scan on show
        self._scan_devices()

    def hide(self):
        """Hide the connection window."""
        dpg.configure_item(self.window_tag, show=False)

    def _scan_devices(self):
        """Scan for available devices."""
        dpg.set_value("connection_status_text", "Scanning...")

        # Scan for devices
        self.devices = self.app.bt_manager.scan_devices()

        # Filter for likely ELM327 devices
        elm_devices = self.app.bt_manager.get_elm327_devices()

        # Update device list
        dpg.delete_item("device_list_group", children_only=True)

        if not self.devices:
            with dpg.group(parent="device_list_group"):
                dpg.add_text("No devices found")
        else:
            with dpg.group(parent="device_list_group"):
                with dpg.table(
                    header_row=True,
                    resizable=True,
                    borders_innerH=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_outerV=True
                ):
                    dpg.add_table_column(label="Port")
                    dpg.add_table_column(label="Description")
                    dpg.add_table_column(label="Select")

                    for device in self.devices:
                        with dpg.table_row():
                            dpg.add_text(device['port'])
                            dpg.add_text(device['description'])
                            dpg.add_radio_button(
                                items=[" "],
                                callback=lambda s, a, u: self._select_device(u),
                                user_data=device,
                                horizontal=True
                            )

        status = f"Found {len(self.devices)} device(s)"
        if elm_devices and len(elm_devices) < len(self.devices):
            status += f" ({len(elm_devices)} likely ELM327)"

        dpg.set_value("connection_status_text", status)

        # Disable connect button
        dpg.configure_item("connect_button", enabled=False)

    def _select_device(self, device: Dict):
        """
        Select a device for connection.

        Args:
            device: Device info dictionary
        """
        self.selected_device = device
        dpg.configure_item("connect_button", enabled=True)
        dpg.set_value(
            "connection_status_text",
            f"Selected: {device['port']} - {device['description']}"
        )

    def _connect(self):
        """Connect to selected device."""
        if not self.selected_device:
            dpg.set_value("connection_status_text", "No device selected")
            return

        port = self.selected_device['port']
        baudrate_str = dpg.get_value("baudrate_combo")
        baudrate = int(baudrate_str)

        dpg.set_value("connection_status_text", f"Connecting to {port}...")

        # Attempt connection
        success = self.app.connect(port, baudrate)

        if success:
            dpg.set_value("connection_status_text", "Connected successfully!")
            # Close window after short delay
            self.hide()
        else:
            dpg.set_value("connection_status_text", "Connection failed!")
