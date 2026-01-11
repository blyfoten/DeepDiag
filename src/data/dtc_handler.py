"""
Diagnostic Trouble Code (DTC) handling and decoding.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class DTC:
    """Diagnostic Trouble Code."""
    code: str
    description: str
    type: str  # 'stored', 'pending', or 'permanent'

    def __str__(self) -> str:
        return f"{self.code}: {self.description}"


class DTCHandler:
    """Handler for diagnostic trouble codes."""

    # Standard DTC descriptions (subset of common codes)
    DTC_DESCRIPTIONS = {
        'P0000': 'No fault',
        'P0100': 'Mass or Volume Air Flow Circuit Malfunction',
        'P0101': 'Mass or Volume Air Flow Circuit Range/Performance Problem',
        'P0102': 'Mass or Volume Air Flow Circuit Low Input',
        'P0103': 'Mass or Volume Air Flow Circuit High Input',
        'P0104': 'Mass or Volume Air Flow Circuit Intermittent',
        'P0105': 'Manifold Absolute Pressure/Barometric Pressure Circuit Malfunction',
        'P0106': 'Manifold Absolute Pressure/Barometric Pressure Circuit Range/Performance Problem',
        'P0107': 'Manifold Absolute Pressure/Barometric Pressure Circuit Low Input',
        'P0108': 'Manifold Absolute Pressure/Barometric Pressure Circuit High Input',
        'P0109': 'Manifold Absolute Pressure/Barometric Pressure Circuit Intermittent',
        'P0110': 'Intake Air Temperature Circuit Malfunction',
        'P0111': 'Intake Air Temperature Circuit Range/Performance Problem',
        'P0112': 'Intake Air Temperature Circuit Low Input',
        'P0113': 'Intake Air Temperature Circuit High Input',
        'P0114': 'Intake Air Temperature Circuit Intermittent',
        'P0115': 'Engine Coolant Temperature Circuit Malfunction',
        'P0116': 'Engine Coolant Temperature Circuit Range/Performance Problem',
        'P0117': 'Engine Coolant Temperature Circuit Low Input',
        'P0118': 'Engine Coolant Temperature Circuit High Input',
        'P0119': 'Engine Coolant Temperature Circuit Intermittent',
        'P0120': 'Throttle Position Sensor/Switch A Circuit Malfunction',
        'P0121': 'Throttle Position Sensor/Switch A Circuit Range/Performance Problem',
        'P0122': 'Throttle Position Sensor/Switch A Circuit Low Input',
        'P0123': 'Throttle Position Sensor/Switch A Circuit High Input',
        'P0124': 'Throttle Position Sensor/Switch A Circuit Intermittent',
        'P0125': 'Insufficient Coolant Temperature for Closed Loop Fuel Control',
        'P0130': 'O2 Sensor Circuit Malfunction (Bank 1, Sensor 1)',
        'P0131': 'O2 Sensor Circuit Low Voltage (Bank 1, Sensor 1)',
        'P0132': 'O2 Sensor Circuit High Voltage (Bank 1, Sensor 1)',
        'P0133': 'O2 Sensor Circuit Slow Response (Bank 1, Sensor 1)',
        'P0134': 'O2 Sensor Circuit No Activity Detected (Bank 1, Sensor 1)',
        'P0135': 'O2 Sensor Heater Circuit Malfunction (Bank 1, Sensor 1)',
        'P0171': 'System Too Lean (Bank 1)',
        'P0172': 'System Too Rich (Bank 1)',
        'P0174': 'System Too Lean (Bank 2)',
        'P0175': 'System Too Rich (Bank 2)',
        'P0200': 'Injector Circuit Malfunction',
        'P0300': 'Random/Multiple Cylinder Misfire Detected',
        'P0301': 'Cylinder 1 Misfire Detected',
        'P0302': 'Cylinder 2 Misfire Detected',
        'P0303': 'Cylinder 3 Misfire Detected',
        'P0304': 'Cylinder 4 Misfire Detected',
        'P0305': 'Cylinder 5 Misfire Detected',
        'P0306': 'Cylinder 6 Misfire Detected',
        'P0307': 'Cylinder 7 Misfire Detected',
        'P0308': 'Cylinder 8 Misfire Detected',
        'P0420': 'Catalyst System Efficiency Below Threshold (Bank 1)',
        'P0430': 'Catalyst System Efficiency Below Threshold (Bank 2)',
        'P0440': 'Evaporative Emission Control System Malfunction',
        'P0441': 'Evaporative Emission Control System Incorrect Purge Flow',
        'P0442': 'Evaporative Emission Control System Leak Detected (Small Leak)',
        'P0443': 'Evaporative Emission Control System Purge Control Valve Circuit Malfunction',
        'P0446': 'Evaporative Emission Control System Vent Control Circuit Malfunction',
        'P0455': 'Evaporative Emission Control System Leak Detected (Large Leak)',
        'P0500': 'Vehicle Speed Sensor Malfunction',
        'P0505': 'Idle Control System Malfunction',
        'P0506': 'Idle Control System RPM Lower Than Expected',
        'P0507': 'Idle Control System RPM Higher Than Expected',
        'P0600': 'Serial Communication Link Malfunction',
        'P0700': 'Transmission Control System Malfunction',
        'P0705': 'Transmission Range Sensor Circuit Malfunction (PRNDL Input)',
        'P0710': 'Transmission Fluid Temperature Sensor Circuit Malfunction',
    }

    def __init__(self):
        """Initialize DTC handler."""
        self.custom_descriptions = {}

    def decode_dtc(self, code: str) -> str:
        """
        Get description for DTC code.

        Args:
            code: DTC code (e.g., 'P0420')

        Returns:
            Description string.
        """
        # Check custom descriptions first
        if code in self.custom_descriptions:
            return self.custom_descriptions[code]

        # Check standard descriptions
        if code in self.DTC_DESCRIPTIONS:
            return self.DTC_DESCRIPTIONS[code]

        # Return generic description based on code prefix
        prefix = code[0]
        if prefix == 'P':
            return 'Powertrain fault'
        elif prefix == 'C':
            return 'Chassis fault'
        elif prefix == 'B':
            return 'Body fault'
        elif prefix == 'U':
            return 'Network/communication fault'
        else:
            return 'Unknown fault'

    def add_custom_description(self, code: str, description: str):
        """
        Add custom DTC description.

        Args:
            code: DTC code
            description: Description text
        """
        self.custom_descriptions[code] = description

    def create_dtc_object(self, code: str, dtc_type: str = 'stored') -> DTC:
        """
        Create DTC object with description.

        Args:
            code: DTC code
            dtc_type: Type of DTC ('stored', 'pending', 'permanent')

        Returns:
            DTC object.
        """
        description = self.decode_dtc(code)
        return DTC(code=code, description=description, type=dtc_type)

    def parse_dtcs(self, codes: List[str], dtc_type: str = 'stored') -> List[DTC]:
        """
        Convert list of DTC codes to DTC objects.

        Args:
            codes: List of DTC code strings
            dtc_type: Type of DTCs

        Returns:
            List of DTC objects.
        """
        return [self.create_dtc_object(code, dtc_type) for code in codes]

    def filter_by_type(self, dtcs: List[DTC], dtc_type: str) -> List[DTC]:
        """
        Filter DTCs by type.

        Args:
            dtcs: List of DTCs
            dtc_type: Type to filter ('stored', 'pending', 'permanent')

        Returns:
            Filtered list.
        """
        return [dtc for dtc in dtcs if dtc.type == dtc_type]

    def get_severity(self, code: str) -> str:
        """
        Estimate severity of DTC.

        Args:
            code: DTC code

        Returns:
            Severity level ('low', 'medium', 'high', 'critical')
        """
        # Simple heuristic based on common codes
        critical_codes = ['P0100', 'P0300', 'P0301', 'P0302', 'P0303', 'P0304']
        high_codes = ['P0171', 'P0172', 'P0420', 'P0430', 'P0500']
        medium_codes = ['P0440', 'P0455', 'P0700']

        if code in critical_codes:
            return 'critical'
        elif code in high_codes:
            return 'high'
        elif code in medium_codes:
            return 'medium'
        else:
            return 'low'
