"""
AI-powered diagnostic window for autonomous troubleshooting.
"""

import dearpygui.dearpygui as dpg
from typing import Optional
import threading
from datetime import datetime
from utils.ai_diagnostic_agent import AIDiagnosticAgent


class AIDiagnosticWindow:
    """AI-powered diagnostic assistant window."""

    def __init__(self, app):
        """
        Initialize AI diagnostic window.

        Args:
            app: Reference to main DiagnosticApp
        """
        self.app = app
        self.window_tag = "ai_diagnostic_window"
        self.agent: Optional[AIDiagnosticAgent] = None
        self.running = False
        self.diagnostic_thread: Optional[threading.Thread] = None

        self._create_window()

    def _create_window(self):
        """Create the AI diagnostic window."""
        with dpg.window(
            label="AI Diagnostic Assistant",
            tag=self.window_tag,
            width=900,
            height=700,
            pos=[190, 10],
            show=False
        ):
            dpg.add_text("AI-Powered Autonomous Diagnostic Agent")
            dpg.add_text("Let the AI interact with your ELM327 to diagnose issues automatically")
            dpg.add_separator()
            dpg.add_spacer(height=10)

            # Task selection
            dpg.add_text("Select Diagnostic Task:")
            dpg.add_radio_button(
                items=[
                    "Auto-diagnose connection issues",
                    "Detect and configure K-line protocol",
                    "Find all supported PIDs",
                    "Test all OBD-II modes",
                    "Diagnose communication errors",
                    "Custom task (describe below)"
                ],
                tag="ai_task_select",
                default_value="Auto-diagnose connection issues"
            )

            dpg.add_spacer(height=5)

            # Custom task input
            dpg.add_text("Custom Task Description:")
            dpg.add_input_text(
                tag="ai_custom_task",
                multiline=True,
                width=-1,
                height=60,
                hint="Describe what you want the AI to investigate..."
            )

            dpg.add_spacer(height=10)

            # API Key section (for future Claude API integration)
            with dpg.collapsing_header(label="API Configuration (Optional)", default_open=False):
                dpg.add_text("For advanced AI features, enter your Anthropic API key:")
                with dpg.group(horizontal=True):
                    dpg.add_input_text(
                        tag="ai_api_key",
                        width=400,
                        password=True,
                        hint="sk-ant-..."
                    )
                    dpg.add_button(
                        label="Save",
                        callback=self._save_api_key,
                        width=80
                    )
                dpg.add_text("Note: Basic diagnostics work without an API key", color=(150, 150, 150))

            dpg.add_spacer(height=10)

            # Control buttons
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Start Diagnostic",
                    callback=self._start_diagnostic,
                    width=150,
                    tag="ai_start_button"
                )
                dpg.add_button(
                    label="Stop",
                    callback=self._stop_diagnostic,
                    width=100,
                    tag="ai_stop_button",
                    enabled=False
                )
                dpg.add_button(
                    label="Clear Log",
                    callback=self._clear_log,
                    width=100
                )
                dpg.add_button(
                    label="Export Report",
                    callback=self._export_report,
                    width=120
                )

            dpg.add_spacer(height=10)
            dpg.add_separator()
            dpg.add_spacer(height=5)

            # Real-time output
            with dpg.tab_bar():
                # AI Activity Tab
                with dpg.tab(label="AI Activity"):
                    dpg.add_text("Real-time AI diagnostic activity:")
                    dpg.add_spacer(height=5)
                    with dpg.child_window(
                        tag="ai_activity_window",
                        width=-1,
                        height=350,
                        border=True
                    ):
                        dpg.add_text(
                            "Click 'Start Diagnostic' to begin AI-powered troubleshooting.\n\n"
                            "The AI will:\n"
                            "• Analyze your connection\n"
                            "• Send diagnostic commands autonomously\n"
                            "• Explain its reasoning\n"
                            "• Provide recommendations\n",
                            tag="ai_activity_text",
                            wrap=870
                        )

                # Command Log Tab
                with dpg.tab(label="Command Log"):
                    with dpg.child_window(
                        tag="ai_command_log_window",
                        width=-1,
                        height=350,
                        border=True
                    ):
                        dpg.add_text(
                            "Command history will appear here...\n",
                            tag="ai_command_log_text",
                            wrap=870
                        )

                # Findings Tab
                with dpg.tab(label="Findings & Recommendations"):
                    with dpg.child_window(
                        tag="ai_findings_window",
                        width=-1,
                        height=350,
                        border=True
                    ):
                        dpg.add_text(
                            "AI findings and recommendations will appear here...\n",
                            tag="ai_findings_text",
                            wrap=870
                        )

            dpg.add_spacer(height=5)

            # Status
            with dpg.group(horizontal=True):
                dpg.add_text("Status:", tag="ai_status_label")
                dpg.add_text("Ready", tag="ai_status_text", color=(200, 200, 200))

            dpg.add_spacer(height=5)

            # Close button
            dpg.add_button(label="Close", callback=self.hide, width=100)

    def show(self):
        """Show the AI diagnostic window."""
        dpg.configure_item(self.window_tag, show=True)

        # Initialize agent if not already done
        if self.agent is None:
            api_key = dpg.get_value("ai_api_key") if dpg.get_value("ai_api_key") else None
            self.agent = AIDiagnosticAgent(self.app, api_key)

    def hide(self):
        """Hide the AI diagnostic window."""
        dpg.configure_item(self.window_tag, show=False)

    def _start_diagnostic(self):
        """Start AI diagnostic session."""
        if not self.app.connected:
            self._append_activity(
                "[ERROR] Cannot start diagnostic - not connected to ELM327 adapter.\n"
                "Please connect first via Connection → Connect\n\n",
                (255, 100, 100)
            )
            return

        if self.running:
            return

        # Get task
        task_selection = dpg.get_value("ai_task_select")
        custom_task = dpg.get_value("ai_custom_task")

        if "Custom task" in task_selection and custom_task:
            task = custom_task
        else:
            task = task_selection

        # Clear previous session
        self._clear_log()

        # Update UI
        dpg.configure_item("ai_start_button", enabled=False)
        dpg.configure_item("ai_stop_button", enabled=True)
        dpg.set_value("ai_status_text", "Running...")
        dpg.configure_item("ai_status_text", color=(100, 255, 100))

        # Start diagnostic in background thread
        self.running = True
        self.diagnostic_thread = threading.Thread(
            target=self._run_diagnostic_thread,
            args=(task,),
            daemon=True
        )
        self.diagnostic_thread.start()

    def _stop_diagnostic(self):
        """Stop AI diagnostic session."""
        self.running = False
        dpg.configure_item("ai_start_button", enabled=True)
        dpg.configure_item("ai_stop_button", enabled=False)
        dpg.set_value("ai_status_text", "Stopped")
        dpg.configure_item("ai_status_text", color=(255, 200, 100))

        self._append_activity("\n[STOPPED] Diagnostic session stopped by user.\n\n", (255, 200, 100))

    def _run_diagnostic_thread(self, task: str):
        """
        Run diagnostic in background thread.

        Args:
            task: Diagnostic task description
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self._append_activity(
            f"=== AI DIAGNOSTIC SESSION STARTED ===\n"
            f"Time: {timestamp}\n"
            f"Task: {task}\n"
            f"{'=' * 50}\n\n",
            (100, 200, 255)
        )

        # Run diagnostic with callback for progress
        try:
            self.agent.run_diagnostic(task, callback=self._diagnostic_callback)

            # Generate summary
            summary = self.agent.get_diagnostic_summary()
            self._append_findings(summary + "\n")

            # Update status
            dpg.set_value("ai_status_text", "Complete")
            dpg.configure_item("ai_status_text", color=(100, 255, 100))

            self._append_activity(
                "\n=== DIAGNOSTIC COMPLETE ===\n"
                "Check the 'Findings & Recommendations' tab for results.\n\n",
                (100, 255, 100)
            )

        except Exception as e:
            self._append_activity(f"\n[ERROR] {str(e)}\n\n", (255, 100, 100))
            dpg.set_value("ai_status_text", "Error")
            dpg.configure_item("ai_status_text", color=(255, 100, 100))

        finally:
            self.running = False
            dpg.configure_item("ai_start_button", enabled=True)
            dpg.configure_item("ai_stop_button", enabled=False)

    def _diagnostic_callback(self, event_type: str, data: any):
        """
        Callback for diagnostic progress updates.

        Args:
            event_type: Type of event ('progress', 'result', 'complete')
            data: Event data
        """
        if event_type == "progress":
            self._append_activity(f"[AI] {data}\n", (200, 200, 255))

        elif event_type == "result":
            description = data.get("description", "")
            result = data.get("result", {})

            # Log to command log
            if "response" in result:
                self._append_command_log(
                    f"{description}\n"
                    f"  Response: {result['response']}\n\n"
                )
            elif "error" in result:
                self._append_command_log(
                    f"{description}\n"
                    f"  ERROR: {result['error']}\n\n",
                    (255, 150, 100)
                )

            # Update activity
            if result.get("success"):
                self._append_activity(f"  ✓ Success\n", (100, 255, 100))
            else:
                self._append_activity(f"  ✗ Failed: {result.get('error', 'Unknown error')}\n", (255, 150, 100))

        elif event_type == "complete":
            self._append_activity(f"\n{data}\n", (100, 255, 100))

    def _clear_log(self):
        """Clear all log windows."""
        dpg.set_value("ai_activity_text", "")
        dpg.set_value("ai_command_log_text", "")
        dpg.set_value("ai_findings_text", "")

    def _append_activity(self, text: str, color: tuple = (255, 255, 255)):
        """Append text to activity log."""
        current = dpg.get_value("ai_activity_text")
        dpg.set_value("ai_activity_text", current + text)

    def _append_command_log(self, text: str, color: tuple = (255, 255, 255)):
        """Append text to command log."""
        current = dpg.get_value("ai_command_log_text")
        dpg.set_value("ai_command_log_text", current + text)

    def _append_findings(self, text: str, color: tuple = (255, 255, 255)):
        """Append text to findings."""
        current = dpg.get_value("ai_findings_text")
        dpg.set_value("ai_findings_text", current + text)

    def _save_api_key(self):
        """Save API key."""
        api_key = dpg.get_value("ai_api_key")
        if api_key:
            # Reinitialize agent with API key
            self.agent = AIDiagnosticAgent(self.app, api_key)
            self._append_activity("[INFO] API key saved. Advanced AI features enabled.\n\n", (100, 255, 100))

    def _export_report(self):
        """Export diagnostic report."""
        if not self.agent or not self.agent.diagnostic_log:
            self._append_activity("[ERROR] No diagnostic data to export.\n\n", (255, 100, 100))
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs/ai_diagnostic_{timestamp}.json"

        try:
            self.agent.export_log(filename)
            self._append_activity(f"[SUCCESS] Report exported to: {filename}\n\n", (100, 255, 100))
        except Exception as e:
            self._append_activity(f"[ERROR] Failed to export: {str(e)}\n\n", (255, 100, 100))
