"""
Utility helper functions.
"""

from typing import List


def format_hex(value: int, width: int = 2) -> str:
    """
    Format integer as hex string.

    Args:
        value: Integer value
        width: Width of hex string (default 2)

    Returns:
        Hex string (e.g., '0x0C')
    """
    return f'0x{value:0{width}X}'


def bytes_to_hex_string(data: List[int], separator: str = ' ') -> str:
    """
    Convert list of bytes to hex string.

    Args:
        data: List of byte values
        separator: Separator between bytes

    Returns:
        Hex string (e.g., '01 0C 1A F8')
    """
    return separator.join([f'{b:02X}' for b in data])


def hex_string_to_bytes(hex_str: str) -> List[int]:
    """
    Convert hex string to list of bytes.

    Args:
        hex_str: Hex string (e.g., '01 0C 1A F8' or '010C1AF8')

    Returns:
        List of byte values
    """
    # Remove spaces and common prefixes
    hex_str = hex_str.replace(' ', '').replace('0x', '').upper()

    # Parse pairs of hex digits
    bytes_list = []
    for i in range(0, len(hex_str), 2):
        if i + 1 < len(hex_str):
            byte_val = int(hex_str[i:i+2], 16)
            bytes_list.append(byte_val)

    return bytes_list


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp value between min and max.

    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value

    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


def format_value(value: any, decimals: int = 2) -> str:
    """
    Format value for display.

    Args:
        value: Value to format
        decimals: Number of decimal places for floats

    Returns:
        Formatted string
    """
    if isinstance(value, float):
        return f'{value:.{decimals}f}'
    elif isinstance(value, int):
        return str(value)
    else:
        return str(value)
