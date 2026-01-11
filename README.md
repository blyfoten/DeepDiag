# DeepDiag - ELM327 Diagnostic Application

A comprehensive Python-based diagnostic application for ELM327 Bluetooth adapters with an ImGui-based GUI.

## Features

- **🤖 AI Diagnostic Assistant**: Autonomous AI agent that troubleshoots your ELM327 connection automatically
- **🔧 K-line Helper**: Specialized troubleshooting for ISO 9141-2 / KWP vehicles
- **ELM327 Communication**: Cross-platform Bluetooth/serial connection support
- **OBD-II Protocol**: Full support for modes 01-04, 07, 09
- **Advanced Diagnostics**: Raw CAN monitoring, multi-ECU support, UDS basics
- **Real-time Visualization**: Live data tables, time-series plots, customizable gauges
- **Debug Console**: Manual command interface for testing and exploration
- **DTC Management**: Read, decode, and clear diagnostic trouble codes
- **Data Logging**: Export session data to CSV
- **Custom PIDs**: Define and use manufacturer-specific PIDs

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py
```

### Quick Start Guide

1. **Connect to your ELM327**
   - Go to `Connection → Connect`
   - Click "Scan" to find devices
   - Select your adapter and click "Connect"

2. **For K-line vehicles** (older vehicles using ISO 9141-2 / KWP):
   - Use `Tools → K-line Helper` for guided troubleshooting
   - Or use `Tools → AI Diagnostic Assistant` for autonomous diagnosis

3. **Test connection**
   - Open `Windows → Debug Console`
   - Try commands: `ATZ`, `ATRV`, `010C` (RPM), `010D` (Speed)

### AI Diagnostic Assistant 🤖

Let the AI troubleshoot your connection automatically:
- Go to `Tools → AI Diagnostic Assistant`
- Select a diagnostic task or describe your own
- Click "Start Diagnostic"
- Watch the AI work and get recommendations

See [AI_DIAGNOSTIC_GUIDE.md](AI_DIAGNOSTIC_GUIDE.md) for detailed usage.

### K-line Helper 🔧

Specialized tool for older K-line vehicles:
- Auto-detects the correct protocol (3, 4, or 5)
- Configures optimal timeout and settings
- Tests connection systematically
- Saves working configuration

## Requirements

- Python 3.8+
- ELM327 Bluetooth adapter
- Vehicle with OBD-II port (1996+ in USA, 2001+ in EU)
- Optional: Anthropic API key for advanced AI features

## Project Structure

- `src/communication/`: Bluetooth and serial communication
- `src/protocol/`: ELM327, OBD-II, and CAN protocols
- `src/data/`: PID definitions, DTC handling, data logging
- `src/gui/`: DearPyGui-based user interface
- `config/`: Configuration files for custom PIDs and layouts

## License

MIT License
