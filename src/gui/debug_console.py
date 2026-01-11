"""
Debug console for raw ELM327 command testing.
"""

import dearpygui.dearpygui as dpg
from datetime import datetime
from typing import List


class DebugConsole:
    """Debug console window for raw command interaction."""

    def __init__(self, app):
        """
        Initialize debug console.

        Args:
            app: Reference to main DiagnosticApp
        """
        self.app = app
        self.window_tag = "debug_console_window"
        self.command_history: List[str] = []
        self.history_index = -1

        self._create_window()

    def _create_window(self):
        """Create the debug console window."""
        with dpg.window(
            label="Debug Console",
            tag=self.window_tag,
            width=800,
            height=600,
            pos=[240, 60],
            show=False
        ):
            dpg.add_text("Raw Command Console - Send AT and OBD commands directly")
            dpg.add_separator()
            dpg.add_spacer(height=5)

            # Output area
            dpg.add_text("Output:")
            with dpg.child_window(
                tag="console_output",
                width=-1,
                height=-100,
                border=True
            ):
                dpg.add_text(
                    "Console ready. Type commands below and press Enter.\n"
                    "Common commands: ATZ (reset), ATI (version), ATRV (voltage), 010C (RPM)",
                    tag="console_text",
                    wrap=780
                )

            dpg.add_spacer(height=5)

            # Input area
            with dpg.group(horizontal=True):
                dpg.add_text("Command:")
                dpg.add_input_text(
                    tag="console_input",
                    width=-150,
                    on_enter=True,
                    callback=self._send_command
                )
                dpg.add_button(
                    label="Send",
                    callback=self._send_command,
                    width=70
                )
                dpg.add_button(
                    label="Clear",
                    callback=self._clear_console,
                    width=70
                )

            dpg.add_spacer(height=5)

            # Quick commands
            dpg.add_text("Quick Commands:")
            with dpg.group(horizontal=True):
                dpg.add_button(label="ATZ (Reset)", callback=lambda: self._quick_command("ATZ"), width=120)
                dpg.add_button(label="ATI (Version)", callback=lambda: self._quick_command("ATI"), width=120)
                dpg.add_button(label="ATRV (Voltage)", callback=lambda: self._quick_command("ATRV"), width=120)
                dpg.add_button(label="ATDP (Protocol)", callback=lambda: self._quick_command("ATDP"), width=120)
                dpg.add_button(label="010C (RPM)", callback=lambda: self._quick_command("010C"), width=120)

    def show(self):
        """Show the debug console window."""
        dpg.configure_item(self.window_tag, show=True)

    def hide(self):
        """Hide the debug console window."""
        dpg.configure_item(self.window_tag, show=False)

    def _send_command(self):
        """Send command from input field."""
        command = dpg.get_value("console_input")

        if not command:
            return

        # Add to history
        self.command_history.append(command)
        self.history_index = len(self.command_history)

        # Check if connected
        if not self.app.connected or not self.app.connection:
            self._append_output(f"\n[ERROR] Not connected to device", color=(255, 100, 100))
            dpg.set_value("console_input", "")
            return

        # Show command
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._append_output(f"\n[{timestamp}] > {command}", color=(100, 200, 255))

        # Send command
        try:
            response = self.app.connection.send_command(command)
            self._append_output(f"  {response}", color=(200, 255, 200))

        except Exception as e:
            self._append_output(f"  ERROR: {str(e)}", color=(255, 100, 100))

        # Clear input
        dpg.set_value("console_input", "")

        # Auto-scroll to bottom
        self._scroll_to_bottom()

    def _quick_command(self, command: str):
        """
        Execute a quick command.

        Args:
            command: Command string to execute
        """
        dpg.set_value("console_input", command)
        self._send_command()

    def _append_output(self, text: str, color: tuple = (255, 255, 255)):
        """
        Append text to console output.

        Args:
            text: Text to append
            color: RGB color tuple
        """
        current_text = dpg.get_value("console_text")
        dpg.set_value("console_text", current_text + text)

    def _clear_console(self):
        """Clear console output."""
        dpg.set_value("console_text", "Console cleared.\n")

    def _scroll_to_bottom(self):
        """Scroll console output to bottom."""
        # Note: DearPyGui doesn't have direct scroll control
        # This is a placeholder for future enhancement
        pass
