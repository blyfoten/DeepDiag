"""
Main DearPyGui application for DeepDiag.
"""

import dearpygui.dearpygui as dpg
from typing import Optional
import threading
import time

from communication import BluetoothManager, ELM327Connection
from protocol import ELM327, OBD2Protocol, CANProtocol, PIDDecoder
from data import DTCHandler, DataLogger, ECUDatabase, CustomPIDManager
from utils import Config

from gui.connection_window import ConnectionWindow
from gui.debug_console import DebugConsole
from gui.kline_helper import KLineHelper
from gui.ai_diagnostic_window import AIDiagnosticWindow


class DiagnosticApp:
    """Main application class for DeepDiag."""

    def __init__(self):
        """Initialize application."""
        # Configuration
        self.config = Config()

        # Communication components
        self.bt_manager = BluetoothManager()
        self.connection: Optional[ELM327Connection] = None
        self.elm327: Optional[ELM327] = None
        self.obd2: Optional[OBD2Protocol] = None
        self.can: Optional[CANProtocol] = None

        # Data components
        self.dtc_handler = DTCHandler()
        self.data_logger = DataLogger()
        self.ecu_database = ECUDatabase()
        self.custom_pid_manager = CustomPIDManager('config/custom_pids.json')
        self.decoder = PIDDecoder()

        # Connection state
        self.connected = False
        self.current_port = None

        # GUI windows
        self.connection_window: Optional[ConnectionWindow] = None
        self.debug_console: Optional[DebugConsole] = None
        self.kline_helper: Optional[KLineHelper] = None
        self.ai_diagnostic: Optional[AIDiagnosticWindow] = None

        # Update thread
        self.update_thread = None
        self.running = False

    def create_gui(self):
        """Create DearPyGui interface."""
        dpg.create_context()

        # Configure viewport
        width = self.config.get('gui.window_width', 1280)
        height = self.config.get('gui.window_height', 720)

        dpg.create_viewport(
            title="DeepDiag - ELM327 Diagnostic Tool",
            width=width,
            height=height
        )

        # Setup theme
        self._setup_theme()

        # Create menu bar
        with dpg.window(label="Main", tag="main_window"):
            with dpg.menu_bar():
                with dpg.menu(label="Connection"):
                    dpg.add_menu_item(
                        label="Connect",
                        callback=self._show_connection_window
                    )
                    dpg.add_menu_item(
                        label="Disconnect",
                        callback=self._disconnect,
                        enabled=False,
                        tag="menu_disconnect"
                    )

                with dpg.menu(label="Windows"):
                    dpg.add_menu_item(
                        label="Debug Console",
                        callback=self._show_debug_console
                    )
                    dpg.add_menu_item(
                        label="Live Data",
                        callback=self._show_live_data,
                        enabled=False,
                        tag="menu_live_data"
                    )
                    dpg.add_menu_item(
                        label="Dashboard",
                        callback=self._show_dashboard,
                        enabled=False,
                        tag="menu_dashboard"
                    )
                    dpg.add_menu_item(
                        label="Plots",
                        callback=self._show_plots,
                        enabled=False,
                        tag="menu_plots"
                    )
                    dpg.add_menu_item(
                        label="DTCs",
                        callback=self._show_dtcs,
                        enabled=False,
                        tag="menu_dtcs"
                    )
                    dpg.add_menu_item(
                        label="CAN Monitor",
                        callback=self._show_can_monitor,
                        enabled=False,
                        tag="menu_can_monitor"
                    )

                with dpg.menu(label="Tools"):
                    dpg.add_menu_item(
                        label="AI Diagnostic Assistant",
                        callback=self._show_ai_diagnostic
                    )
                    dpg.add_separator()
                    dpg.add_menu_item(
                        label="K-line Helper",
                        callback=self._show_kline_helper
                    )

                with dpg.menu(label="Help"):
                    dpg.add_menu_item(label="About", callback=self._show_about)

            # Status bar
            with dpg.group(horizontal=True):
                dpg.add_text("Status:", tag="status_label")
                dpg.add_text("Disconnected", tag="status_text", color=(255, 100, 100))
                dpg.add_spacer(width=20)
                dpg.add_text("Port:", tag="port_label")
                dpg.add_text("-", tag="port_text")
                dpg.add_spacer(width=20)
                dpg.add_text("Voltage:", tag="voltage_label")
                dpg.add_text("-", tag="voltage_text")

        # Set main window as primary
        dpg.set_primary_window("main_window", True)

        # Create windows (hidden initially)
        self.connection_window = ConnectionWindow(self)
        self.debug_console = DebugConsole(self)
        self.kline_helper = KLineHelper(self)
        self.ai_diagnostic = AIDiagnosticWindow(self)

        # Load custom PIDs
        self.custom_pid_manager.load_from_json()

    def run(self):
        """Run the application."""
        dpg.setup_dearpygui()
        dpg.show_viewport()

        self.running = True

        # Start update thread
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()

        # Main rendering loop
        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()

        self.running = False
        self.cleanup()

    def cleanup(self):
        """Cleanup on exit."""
        self.running = False

        if self.connected:
            self._disconnect()

        if self.data_logger.is_logging():
            self.data_logger.stop_logging()

        dpg.destroy_context()

    def connect(self, port: str, baudrate: int = 38400):
        """
        Connect to ELM327 device.

        Args:
            port: Serial port name
            baudrate: Connection speed
        """
        try:
            # Create connection
            timeout = self.config.get('connection.timeout', 3.0)
            self.connection = ELM327Connection(port, baudrate, timeout)

            # Connect
            self.connection.connect()

            # Initialize ELM327
            self.elm327 = ELM327(self.connection)
            protocol = self.config.get('elm327.default_protocol', '0')
            echo = self.config.get('elm327.echo', False)
            headers = self.config.get('elm327.headers', False)
            spaces = self.config.get('elm327.spaces', True)

            self.elm327.initialize(protocol, echo, headers, spaces)

            # Create protocol handlers
            self.obd2 = OBD2Protocol(self.connection)
            self.can = CANProtocol(self.connection)

            # Update state
            self.connected = True
            self.current_port = port

            # Update UI
            self._update_connection_status()

            return True

        except Exception as e:
            self._show_error(f"Connection failed: {str(e)}")
            return False

    def _disconnect(self):
        """Disconnect from device."""
        if self.connection:
            self.connection.disconnect()

        self.connected = False
        self.current_port = None
        self.connection = None
        self.elm327 = None
        self.obd2 = None
        self.can = None

        self._update_connection_status()

    def _update_connection_status(self):
        """Update connection status in UI."""
        if self.connected:
            dpg.set_value("status_text", "Connected")
            dpg.configure_item("status_text", color=(100, 255, 100))
            dpg.set_value("port_text", self.current_port)

            if self.elm327 and self.elm327.voltage:
                dpg.set_value("voltage_text", f"{self.elm327.voltage:.1f}V")

            # Enable menu items
            dpg.configure_item("menu_disconnect", enabled=True)
            dpg.configure_item("menu_live_data", enabled=True)
            dpg.configure_item("menu_dashboard", enabled=True)
            dpg.configure_item("menu_plots", enabled=True)
            dpg.configure_item("menu_dtcs", enabled=True)
            dpg.configure_item("menu_can_monitor", enabled=True)

        else:
            dpg.set_value("status_text", "Disconnected")
            dpg.configure_item("status_text", color=(255, 100, 100))
            dpg.set_value("port_text", "-")
            dpg.set_value("voltage_text", "-")

            # Disable menu items
            dpg.configure_item("menu_disconnect", enabled=False)
            dpg.configure_item("menu_live_data", enabled=False)
            dpg.configure_item("menu_dashboard", enabled=False)
            dpg.configure_item("menu_plots", enabled=False)
            dpg.configure_item("menu_dtcs", enabled=False)
            dpg.configure_item("menu_can_monitor", enabled=False)

    def _update_loop(self):
        """Background update loop."""
        while self.running:
            if self.connected and self.elm327:
                try:
                    # Update voltage periodically
                    voltage = self.elm327.get_voltage()
                    dpg.set_value("voltage_text", f"{voltage:.1f}V")

                except Exception:
                    pass

            time.sleep(5.0)  # Update every 5 seconds

    def _setup_theme(self):
        """Setup DearPyGui theme."""
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 5)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 5)
                dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 5)
                dpg.add_theme_style(dpg.mvStyleVar_TabRounding, 5)

        dpg.bind_theme(global_theme)

    # Menu callbacks
    def _show_connection_window(self):
        """Show connection window."""
        if self.connection_window:
            self.connection_window.show()

    def _show_debug_console(self):
        """Show debug console."""
        if self.debug_console:
            self.debug_console.show()

    def _show_kline_helper(self):
        """Show K-line troubleshooting helper."""
        if self.kline_helper:
            self.kline_helper.show()

    def _show_ai_diagnostic(self):
        """Show AI diagnostic assistant."""
        if self.ai_diagnostic:
            self.ai_diagnostic.show()

    def _show_live_data(self):
        """Show live data window."""
        # TODO: Implement in Phase 5
        pass

    def _show_dashboard(self):
        """Show dashboard window."""
        # TODO: Implement in Phase 6
        pass

    def _show_plots(self):
        """Show plots window."""
        # TODO: Implement in Phase 7
        pass

    def _show_dtcs(self):
        """Show DTCs window."""
        # TODO: Implement in Phase 8
        pass

    def _show_can_monitor(self):
        """Show CAN monitor window."""
        # TODO: Implement in Phase 9
        pass

    def _show_about(self):
        """Show about dialog."""
        if not dpg.does_item_exist("about_window"):
            with dpg.window(label="About DeepDiag", tag="about_window", modal=True,
                           width=400, height=200, pos=[440, 260]):
                dpg.add_text("DeepDiag - ELM327 Diagnostic Tool")
                dpg.add_spacer(height=10)
                dpg.add_text("Version 1.0.0")
                dpg.add_spacer(height=10)
                dpg.add_text("A comprehensive diagnostic application for")
                dpg.add_text("ELM327 Bluetooth adapters with ImGui GUI.")
                dpg.add_spacer(height=20)
                dpg.add_button(label="Close", callback=lambda: dpg.delete_item("about_window"))

    def _show_error(self, message: str):
        """Show error dialog."""
        tag = "error_window"
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)

        with dpg.window(label="Error", tag=tag, modal=True,
                       width=400, height=150, pos=[440, 285]):
            dpg.add_text(message, wrap=380)
            dpg.add_spacer(height=20)
            dpg.add_button(label="OK", callback=lambda: dpg.delete_item(tag))
