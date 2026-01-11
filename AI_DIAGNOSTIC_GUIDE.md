# AI Diagnostic Assistant Guide

## Overview

The AI Diagnostic Assistant is an autonomous agent that can interact directly with your ELM327 adapter to diagnose connection issues, test protocols, and troubleshoot problems automatically.

## How It Works

The AI agent has direct access to send commands to your ELM327 adapter through these tools:

1. **send_command** - Send AT commands (like ATZ, ATSP3) or OBD-II commands (like 0100, 010C)
2. **get_connection_status** - Check current connection state
3. **get_protocol_info** - Get protocol information
4. **report_finding** - Report findings and recommendations

The AI will:
- Analyze your connection systematically
- Send diagnostic commands autonomously
- Explain its reasoning at each step
- Adapt based on responses
- Provide specific recommendations

## Quick Start

1. **Connect to your ELM327 adapter first**
   - Go to Connection → Connect
   - Select your device and connect

2. **Open AI Diagnostic Assistant**
   - Tools → AI Diagnostic Assistant

3. **Select a diagnostic task:**
   - Auto-diagnose connection issues (recommended for K-line)
   - Detect and configure K-line protocol
   - Find all supported PIDs
   - Test all OBD-II modes
   - Diagnose communication errors
   - Custom task (describe your own)

4. **Click "Start Diagnostic"**
   - Watch the AI work in real-time
   - Check the "Findings & Recommendations" tab when complete

## Features

### Pre-built Diagnostic Tasks

**Auto-diagnose connection issues** (Best for K-line vehicles)
- Tests adapter connectivity
- Tries different protocols (3, 4, 5 for K-line)
- Configures optimal settings
- Reports what works

**Detect and configure K-line protocol**
- Specifically for ISO 9141-2 / KWP vehicles
- Tests protocols 3, 4, and 5
- Sets appropriate timeouts
- Configures headers and timing

**Find all supported PIDs**
- Queries PID support bitmaps (0100, 0120, 0140, etc.)
- Lists all available PIDs
- Tests each one for response

**Test all OBD-II modes**
- Tests Mode 01 (current data)
- Tests Mode 03 (read DTCs)
- Tests Mode 07 (pending DTCs)
- Tests Mode 09 (vehicle info)

### Custom Tasks

You can describe any diagnostic task in plain English:

Examples:
- "My vehicle won't respond on protocol 3, help me find the right protocol"
- "Test if my vehicle supports RPM and speed PIDs"
- "I'm getting timeouts on all queries, diagnose why"
- "Configure my K-line vehicle for optimal performance"

## Real-Time Monitoring

The AI window has three tabs:

### AI Activity
Shows what the AI is thinking and doing in real-time:
- Current action
- Reasoning
- Success/failure status

### Command Log
Complete history of commands sent and responses received:
- Timestamp
- Command
- Response
- Errors (if any)

### Findings & Recommendations
Final diagnostic report:
- Summary of what was tested
- What works and what doesn't
- Specific recommendations
- Configuration settings

## Advanced Features (Optional)

### Claude API Integration

For enhanced AI capabilities, you can provide an Anthropic API key:

1. Get an API key from https://console.anthropic.com
2. Enter it in "API Configuration" section
3. Click "Save"

With API integration, the AI will:
- Use advanced reasoning
- Provide more detailed explanations
- Handle complex multi-step diagnostics
- Learn from previous sessions

**Note:** Basic diagnostics work without an API key using pre-programmed sequences.

## Example Session (K-line Vehicle)

```
=== AI DIAGNOSTIC SESSION STARTED ===
Task: Auto-diagnose connection issues

[AI] Checking connection status...
  ✓ Success - Connected to COM5

[AI] Getting adapter version...
  Response: ELM327 v2.1
  ✓ Success

[AI] Reading voltage...
  Response: 13.7V
  ✓ Success

[AI] Checking current protocol...
  Response: AUTO
  ✓ Success

[AI] Setting protocol to ISO 9141-2...
  Response: OK
  ✓ Success

[AI] Increasing timeout for K-line...
  Response: OK
  ✓ Success

[AI] Enabling headers...
  Response: OK
  ✓ Success

[AI] Testing with supported PIDs query...
  Response: 48 6B 10 41 00 BE 1F B8 11
  ✓ Success

=== FINDINGS ===
[SUCCESS] Protocol 3 (ISO 9141-2) works with your vehicle
[INFO] Recommended timeout: 255 (1020ms)
[INFO] Headers: ON for better diagnostics
[SUCCESS] Vehicle supports PIDs: 01, 03, 04, 05, 06, 07, 0B, 0C, 0D, 0E, 0F, 10, 11, 13, 15, 1C, 1F, 20

=== RECOMMENDATIONS ===
1. Keep protocol set to 3 (ATSP3)
2. Use maximum timeout (ATST FF)
3. Enable adaptive timing mode 2 (ATAT2)
4. Your vehicle supports standard OBD-II PIDs
5. Try queries: 010C (RPM), 010D (Speed), 0105 (Coolant Temp)
```

## Export Reports

Click "Export Report" to save the full diagnostic session:
- JSON format
- Saved to `logs/ai_diagnostic_TIMESTAMP.json`
- Contains all commands, responses, and findings
- Useful for sharing or later analysis

## Tips for Best Results

1. **Connect first** - Always connect to your ELM327 before starting diagnostics
2. **Vehicle ignition ON** - K-line vehicles need ignition on (engine doesn't need to run)
3. **Be patient** - K-line protocols are slower than CAN, let the AI work
4. **Check all tabs** - Findings tab has the summary, Command Log shows details
5. **Export reports** - Save successful configurations for later reference

## Troubleshooting

**"Not connected to ELM327 adapter"**
- Connect via Connection → Connect first

**AI stops or gets stuck**
- Click "Stop" and try again
- Check Debug Console for manual testing
- Try a different diagnostic task

**No PIDs found**
- Vehicle may not support standard OBD-II
- Try manufacturer-specific protocols
- Check vehicle manual for OBD-II compliance

## Future Enhancements

Planned features:
- Integration with Claude API for advanced reasoning
- Learning from successful configurations
- Vehicle-specific diagnostic libraries
- Automated DTC analysis
- Performance optimization suggestions
