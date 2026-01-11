"""
AI-powered diagnostic agent for autonomous ELM327 troubleshooting.
Uses Claude API (or compatible) to intelligently diagnose and fix connection issues.
"""

import json
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime


class AIDiagnosticAgent:
    """
    AI agent that can autonomously interact with ELM327 adapter to diagnose issues.
    """

    def __init__(self, app, api_key: Optional[str] = None):
        """
        Initialize AI diagnostic agent.

        Args:
            app: Reference to main DiagnosticApp
            api_key: Anthropic API key (optional, will prompt if not provided)
        """
        self.app = app
        self.api_key = api_key
        self.conversation_history: List[Dict] = []
        self.diagnostic_log: List[Dict] = []
        self.running = False

        # Tools available to the AI
        self.tools = [
            {
                "name": "send_command",
                "description": "Send a command to the ELM327 adapter and receive response. Use this to send AT commands (like ATZ, ATSP3, etc.) or OBD-II commands (like 0100, 010C, etc.)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The command to send (e.g., 'ATZ', 'ATSP3', '0100')"
                        },
                        "delay": {
                            "type": "number",
                            "description": "Optional delay in seconds after sending (default 0.1)",
                            "default": 0.1
                        }
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "get_connection_status",
                "description": "Check if currently connected to ELM327 adapter and get connection details",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_protocol_info",
                "description": "Get current protocol information from ELM327",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "report_finding",
                "description": "Report a diagnostic finding or recommendation to the user",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "severity": {
                            "type": "string",
                            "enum": ["info", "success", "warning", "error"],
                            "description": "Severity level of the finding"
                        },
                        "message": {
                            "type": "string",
                            "description": "The finding or recommendation message"
                        }
                    },
                    "required": ["severity", "message"]
                }
            }
        ]

    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call from the AI.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            Tool execution result
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        if tool_name == "send_command":
            command = tool_input["command"]
            delay = tool_input.get("delay", 0.1)

            # Log the action
            self.diagnostic_log.append({
                "timestamp": timestamp,
                "type": "command",
                "command": command,
                "delay": delay
            })

            # Execute
            if not self.app.connected or not self.app.connection:
                result = {"success": False, "error": "Not connected to ELM327 adapter"}
            else:
                try:
                    response = self.app.connection.send_command(command, delay=delay)
                    result = {"success": True, "response": response}

                    # Log response
                    self.diagnostic_log.append({
                        "timestamp": timestamp,
                        "type": "response",
                        "response": response
                    })
                except Exception as e:
                    result = {"success": False, "error": str(e)}

            return result

        elif tool_name == "get_connection_status":
            status = {
                "connected": self.app.connected,
                "port": self.app.current_port,
                "voltage": self.app.elm327.voltage if self.app.elm327 else None,
                "protocol": self.app.elm327.protocol if self.app.elm327 else None
            }

            self.diagnostic_log.append({
                "timestamp": timestamp,
                "type": "status_check",
                "status": status
            })

            return status

        elif tool_name == "get_protocol_info":
            if not self.app.connected or not self.app.connection:
                return {"error": "Not connected"}

            try:
                protocol = self.app.connection.send_command("ATDP")
                protocol_num = self.app.connection.send_command("ATDPN")

                result = {
                    "protocol": protocol,
                    "protocol_number": protocol_num
                }

                self.diagnostic_log.append({
                    "timestamp": timestamp,
                    "type": "protocol_check",
                    "result": result
                })

                return result
            except Exception as e:
                return {"error": str(e)}

        elif tool_name == "report_finding":
            severity = tool_input["severity"]
            message = tool_input["message"]

            self.diagnostic_log.append({
                "timestamp": timestamp,
                "type": "finding",
                "severity": severity,
                "message": message
            })

            return {"reported": True}

        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def get_system_prompt(self, task: str) -> str:
        """
        Generate system prompt for the AI agent.

        Args:
            task: The diagnostic task to perform

        Returns:
            System prompt string
        """
        return f"""You are an expert automotive diagnostic AI assistant specializing in ELM327 OBD-II adapters. You have direct access to send commands to an ELM327 adapter via serial connection.

Your current task: {task}

CAPABILITIES:
You can use the following tools to diagnose and troubleshoot:
1. send_command - Send AT commands (ATZ, ATSP, ATRV, etc.) or OBD-II commands (0100, 010C, etc.)
2. get_connection_status - Check connection state
3. get_protocol_info - Get current protocol information
4. report_finding - Report findings to the user

ELM327 KNOWLEDGE:
- AT Commands: ATZ (reset), ATI (version), ATRV (voltage), ATSP (set protocol), ATDP (describe protocol)
- Protocols: 0=Auto, 3=ISO9141, 4=KWP5BAUD, 5=KWPFast, 6=CAN11/500, 7=CAN29/500, 8=CAN11/250, 9=CAN29/250
- OBD-II: 01XX (current data), 03 (read DTCs), 04 (clear DTCs), 09XX (vehicle info)
- Timeouts: ATST (set timeout, hex value x4ms), max FF (1020ms)
- Headers: ATH1 (on), ATH0 (off)
- Adaptive timing: ATAT0/1/2

K-LINE TROUBLESHOOTING (ISO 9141-2 / KWP):
- K-line vehicles need longer timeouts (ATST FF)
- Try protocols 3, 4, 5 in order
- Often need headers enabled initially (ATH1)
- Slower than CAN, be patient
- Vehicle ignition must be ON

DIAGNOSTIC APPROACH:
1. Check connection status first
2. Verify adapter responds (ATI, ATRV)
3. Determine appropriate protocol
4. Configure settings (timeout, headers, etc.)
5. Test with 0100 (supported PIDs)
6. Test specific PIDs if needed
7. Report findings with recommendations

IMPORTANT:
- Test one thing at a time
- Explain your reasoning before each action
- If something fails, try alternatives
- Report findings as you discover them
- Be systematic and thorough

Begin your diagnostic work now."""

    def run_diagnostic(self, task: str, callback: Optional[Callable] = None) -> List[Dict]:
        """
        Run an AI-powered diagnostic session.

        Args:
            task: Description of the diagnostic task
            callback: Optional callback for progress updates

        Returns:
            Diagnostic log
        """
        self.running = True
        self.diagnostic_log = []

        # This is a simplified version - in production, integrate with Anthropic API
        # For now, return a mock diagnostic sequence
        self._mock_diagnostic_session(task, callback)

        self.running = False
        return self.diagnostic_log

    def _mock_diagnostic_session(self, task: str, callback: Optional[Callable] = None):
        """
        Mock diagnostic session (replace with actual API integration).

        Args:
            task: Diagnostic task
            callback: Progress callback
        """
        # Example diagnostic sequence
        steps = [
            ("Checking connection status...", "get_connection_status", {}),
            ("Getting adapter version...", "send_command", {"command": "ATI"}),
            ("Reading voltage...", "send_command", {"command": "ATRV"}),
            ("Checking current protocol...", "send_command", {"command": "ATDP"}),
            ("Setting protocol to ISO 9141-2...", "send_command", {"command": "ATSP3"}),
            ("Increasing timeout for K-line...", "send_command", {"command": "ATST FF"}),
            ("Enabling headers...", "send_command", {"command": "ATH1"}),
            ("Testing with supported PIDs query...", "send_command", {"command": "0100"}),
        ]

        for description, tool, params in steps:
            if callback:
                callback("progress", description)

            result = self.execute_tool(tool, params)

            if callback:
                callback("result", {"description": description, "result": result})

        # Final report
        if callback:
            callback("complete", "Diagnostic session complete. Check log for details.")

    def get_diagnostic_summary(self) -> str:
        """
        Generate a summary of the diagnostic session.

        Returns:
            Summary string
        """
        if not self.diagnostic_log:
            return "No diagnostic data available."

        summary = "=== DIAGNOSTIC SUMMARY ===\n\n"

        # Count commands and responses
        commands = [log for log in self.diagnostic_log if log["type"] == "command"]
        responses = [log for log in self.diagnostic_log if log["type"] == "response"]
        findings = [log for log in self.diagnostic_log if log["type"] == "finding"]

        summary += f"Commands sent: {len(commands)}\n"
        summary += f"Responses received: {len(responses)}\n"
        summary += f"Findings: {len(findings)}\n\n"

        # List findings
        if findings:
            summary += "=== FINDINGS ===\n"
            for finding in findings:
                severity = finding["severity"].upper()
                message = finding["message"]
                summary += f"[{severity}] {message}\n"

        return summary

    def export_log(self, filename: str):
        """
        Export diagnostic log to JSON file.

        Args:
            filename: Output filename
        """
        with open(filename, 'w') as f:
            json.dump(self.diagnostic_log, f, indent=2)
