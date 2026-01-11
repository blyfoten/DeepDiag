"""
Standard OBD-II PID definitions with decoding formulas.
"""

from typing import Callable, Any, List


class PIDDefinition:
    """Definition for a single PID."""

    def __init__(self, pid: int, name: str, description: str, unit: str,
                 decoder: Callable[[List[int]], Any], num_bytes: int = 1,
                 min_val: float = 0, max_val: float = 100):
        """
        Initialize PID definition.

        Args:
            pid: PID number (0x00-0xFF)
            name: Short name
            description: Full description
            unit: Unit of measurement
            decoder: Function to decode bytes to value
            num_bytes: Expected number of data bytes
            min_val: Minimum value for gauges
            max_val: Maximum value for gauges
        """
        self.pid = pid
        self.name = name
        self.description = description
        self.unit = unit
        self.decoder = decoder
        self.num_bytes = num_bytes
        self.min_val = min_val
        self.max_val = max_val


# Decoder functions
def decode_percent(data: List[int]) -> float:
    """Decode percentage (A*100/255)."""
    return (data[0] * 100.0) / 255.0


def decode_temp(data: List[int]) -> int:
    """Decode temperature (A-40)."""
    return data[0] - 40


def decode_rpm(data: List[int]) -> float:
    """Decode RPM ((A*256+B)/4)."""
    return ((data[0] * 256) + data[1]) / 4.0


def decode_speed(data: List[int]) -> int:
    """Decode vehicle speed (A)."""
    return data[0]


def decode_short_trim(data: List[int]) -> float:
    """Decode fuel trim ((A-128)*100/128)."""
    return ((data[0] - 128) * 100.0) / 128.0


def decode_pressure(data: List[int]) -> int:
    """Decode pressure (A)."""
    return data[0]


def decode_pressure_3byte(data: List[int]) -> float:
    """Decode 3-byte pressure ((A*256+B)*0.079)."""
    return ((data[0] * 256) + data[1]) * 0.079


def decode_maf(data: List[int]) -> float:
    """Decode MAF flow rate ((A*256+B)/100)."""
    return ((data[0] * 256) + data[1]) / 100.0


def decode_timing_advance(data: List[int]) -> float:
    """Decode timing advance ((A-128)/2)."""
    return (data[0] - 128) / 2.0


def decode_o2_voltage(data: List[int]) -> float:
    """Decode O2 sensor voltage (A/200)."""
    return data[0] / 200.0


def decode_o2_trim(data: List[int]) -> float:
    """Decode O2 sensor fuel trim ((B-128)*100/128)."""
    return ((data[1] - 128) * 100.0) / 128.0


def decode_runtime(data: List[int]) -> int:
    """Decode runtime since engine start (A*256+B)."""
    return (data[0] * 256) + data[1]


def decode_distance(data: List[int]) -> int:
    """Decode distance (A*256+B)."""
    return (data[0] * 256) + data[1]


def decode_evap_pressure(data: List[int]) -> float:
    """Decode EVAP pressure (((A*256+B)-32768)/4)."""
    return (((data[0] * 256) + data[1]) - 32768) / 4.0


def decode_fuel_level(data: List[int]) -> float:
    """Decode fuel level (A*100/255)."""
    return (data[0] * 100.0) / 255.0


def decode_absolute_load(data: List[int]) -> float:
    """Decode absolute load ((A*256+B)*100/255)."""
    return ((data[0] * 256) + data[1]) * 100.0 / 255.0


def decode_equiv_ratio(data: List[int]) -> float:
    """Decode equivalence ratio ((A*256+B)/32768)."""
    return ((data[0] * 256) + data[1]) / 32768.0


def decode_bitmap(data: List[int]) -> str:
    """Decode bitmap (return hex string)."""
    return ' '.join([f'{b:02X}' for b in data])


# Standard Mode 01 PIDs
STANDARD_PIDS = {
    0x00: PIDDefinition(
        pid=0x00,
        name="PIDs_supported",
        description="PIDs supported [01-20]",
        unit="",
        decoder=decode_bitmap,
        num_bytes=4
    ),
    0x01: PIDDefinition(
        pid=0x01,
        name="Monitor_status",
        description="Monitor status since DTCs cleared",
        unit="",
        decoder=decode_bitmap,
        num_bytes=4
    ),
    0x03: PIDDefinition(
        pid=0x03,
        name="Fuel_system_status",
        description="Fuel system status",
        unit="",
        decoder=decode_bitmap,
        num_bytes=2
    ),
    0x04: PIDDefinition(
        pid=0x04,
        name="Engine_load",
        description="Calculated engine load",
        unit="%",
        decoder=decode_percent,
        num_bytes=1,
        min_val=0,
        max_val=100
    ),
    0x05: PIDDefinition(
        pid=0x05,
        name="Coolant_temp",
        description="Engine coolant temperature",
        unit="°C",
        decoder=decode_temp,
        num_bytes=1,
        min_val=-40,
        max_val=215
    ),
    0x06: PIDDefinition(
        pid=0x06,
        name="Short_fuel_trim_1",
        description="Short term fuel trim - Bank 1",
        unit="%",
        decoder=decode_short_trim,
        num_bytes=1,
        min_val=-100,
        max_val=99.2
    ),
    0x07: PIDDefinition(
        pid=0x07,
        name="Long_fuel_trim_1",
        description="Long term fuel trim - Bank 1",
        unit="%",
        decoder=decode_short_trim,
        num_bytes=1,
        min_val=-100,
        max_val=99.2
    ),
    0x08: PIDDefinition(
        pid=0x08,
        name="Short_fuel_trim_2",
        description="Short term fuel trim - Bank 2",
        unit="%",
        decoder=decode_short_trim,
        num_bytes=1,
        min_val=-100,
        max_val=99.2
    ),
    0x09: PIDDefinition(
        pid=0x09,
        name="Long_fuel_trim_2",
        description="Long term fuel trim - Bank 2",
        unit="%",
        decoder=decode_short_trim,
        num_bytes=1,
        min_val=-100,
        max_val=99.2
    ),
    0x0A: PIDDefinition(
        pid=0x0A,
        name="Fuel_pressure",
        description="Fuel pressure",
        unit="kPa",
        decoder=lambda d: d[0] * 3,
        num_bytes=1,
        min_val=0,
        max_val=765
    ),
    0x0B: PIDDefinition(
        pid=0x0B,
        name="Intake_pressure",
        description="Intake manifold absolute pressure",
        unit="kPa",
        decoder=decode_pressure,
        num_bytes=1,
        min_val=0,
        max_val=255
    ),
    0x0C: PIDDefinition(
        pid=0x0C,
        name="Engine_RPM",
        description="Engine RPM",
        unit="RPM",
        decoder=decode_rpm,
        num_bytes=2,
        min_val=0,
        max_val=16383
    ),
    0x0D: PIDDefinition(
        pid=0x0D,
        name="Vehicle_speed",
        description="Vehicle speed",
        unit="km/h",
        decoder=decode_speed,
        num_bytes=1,
        min_val=0,
        max_val=255
    ),
    0x0E: PIDDefinition(
        pid=0x0E,
        name="Timing_advance",
        description="Timing advance",
        unit="° before TDC",
        decoder=decode_timing_advance,
        num_bytes=1,
        min_val=-64,
        max_val=63.5
    ),
    0x0F: PIDDefinition(
        pid=0x0F,
        name="Intake_temp",
        description="Intake air temperature",
        unit="°C",
        decoder=decode_temp,
        num_bytes=1,
        min_val=-40,
        max_val=215
    ),
    0x10: PIDDefinition(
        pid=0x10,
        name="MAF_flow",
        description="Mass air flow rate",
        unit="g/s",
        decoder=decode_maf,
        num_bytes=2,
        min_val=0,
        max_val=655.35
    ),
    0x11: PIDDefinition(
        pid=0x11,
        name="Throttle_position",
        description="Throttle position",
        unit="%",
        decoder=decode_percent,
        num_bytes=1,
        min_val=0,
        max_val=100
    ),
    0x1F: PIDDefinition(
        pid=0x1F,
        name="Runtime",
        description="Run time since engine start",
        unit="s",
        decoder=decode_runtime,
        num_bytes=2,
        min_val=0,
        max_val=65535
    ),
    0x21: PIDDefinition(
        pid=0x21,
        name="Distance_with_MIL",
        description="Distance traveled with MIL on",
        unit="km",
        decoder=decode_distance,
        num_bytes=2,
        min_val=0,
        max_val=65535
    ),
    0x2F: PIDDefinition(
        pid=0x2F,
        name="Fuel_level",
        description="Fuel tank level input",
        unit="%",
        decoder=decode_fuel_level,
        num_bytes=1,
        min_val=0,
        max_val=100
    ),
    0x33: PIDDefinition(
        pid=0x33,
        name="Barometric_pressure",
        description="Absolute barometric pressure",
        unit="kPa",
        decoder=decode_pressure,
        num_bytes=1,
        min_val=0,
        max_val=255
    ),
    0x42: PIDDefinition(
        pid=0x42,
        name="Control_module_voltage",
        description="Control module voltage",
        unit="V",
        decoder=lambda d: ((d[0] * 256) + d[1]) / 1000.0,
        num_bytes=2,
        min_val=0,
        max_val=65.535
    ),
    0x43: PIDDefinition(
        pid=0x43,
        name="Absolute_load",
        description="Absolute load value",
        unit="%",
        decoder=decode_absolute_load,
        num_bytes=2,
        min_val=0,
        max_val=25700
    ),
    0x44: PIDDefinition(
        pid=0x44,
        name="Commanded_equiv_ratio",
        description="Commanded equivalence ratio",
        unit="",
        decoder=decode_equiv_ratio,
        num_bytes=2,
        min_val=0,
        max_val=2
    ),
    0x45: PIDDefinition(
        pid=0x45,
        name="Relative_throttle",
        description="Relative throttle position",
        unit="%",
        decoder=decode_percent,
        num_bytes=1,
        min_val=0,
        max_val=100
    ),
    0x46: PIDDefinition(
        pid=0x46,
        name="Ambient_temp",
        description="Ambient air temperature",
        unit="°C",
        decoder=decode_temp,
        num_bytes=1,
        min_val=-40,
        max_val=215
    ),
    0x49: PIDDefinition(
        pid=0x49,
        name="Accelerator_pedal_D",
        description="Accelerator pedal position D",
        unit="%",
        decoder=decode_percent,
        num_bytes=1,
        min_val=0,
        max_val=100
    ),
    0x4C: PIDDefinition(
        pid=0x4C,
        name="Commanded_throttle",
        description="Commanded throttle actuator",
        unit="%",
        decoder=decode_percent,
        num_bytes=1,
        min_val=0,
        max_val=100
    ),
    0x51: PIDDefinition(
        pid=0x51,
        name="Fuel_type",
        description="Fuel type",
        unit="",
        decoder=lambda d: d[0],
        num_bytes=1
    ),
    0x5C: PIDDefinition(
        pid=0x5C,
        name="Engine_oil_temp",
        description="Engine oil temperature",
        unit="°C",
        decoder=decode_temp,
        num_bytes=1,
        min_val=-40,
        max_val=215
    ),
}


def get_pid_by_name(name: str) -> PIDDefinition:
    """Get PID definition by name."""
    for pid_def in STANDARD_PIDS.values():
        if pid_def.name == name:
            return pid_def
    raise KeyError(f"PID with name '{name}' not found")


def get_common_pids() -> List[int]:
    """Get list of commonly used PIDs for quick access."""
    return [
        0x0C,  # RPM
        0x0D,  # Vehicle speed
        0x05,  # Coolant temp
        0x0F,  # Intake temp
        0x11,  # Throttle position
        0x04,  # Engine load
        0x10,  # MAF
        0x2F,  # Fuel level
        0x0B,  # Intake pressure
    ]
