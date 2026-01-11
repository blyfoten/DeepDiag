"""
Custom PID management and loading from JSON configuration.
"""

import json
from typing import Dict, List, Callable, Any
from pathlib import Path
from data.pid_definitions import PIDDefinition


class CustomPIDManager:
    """Manager for custom (manufacturer-specific) PIDs."""

    def __init__(self, config_path: str = None):
        """
        Initialize custom PID manager.

        Args:
            config_path: Path to JSON configuration file
        """
        self.config_path = config_path
        self.custom_pids: Dict[tuple, PIDDefinition] = {}

    def load_from_json(self, file_path: str = None):
        """
        Load custom PIDs from JSON file.

        Args:
            file_path: Path to JSON file (uses config_path if not specified)
        """
        path = file_path or self.config_path

        if not path or not Path(path).exists():
            return

        try:
            with open(path, 'r') as f:
                data = json.load(f)

            for pid_data in data.get('pids', []):
                self._add_pid_from_dict(pid_data)

        except Exception as e:
            print(f"Error loading custom PIDs: {str(e)}")

    def save_to_json(self, file_path: str = None):
        """
        Save custom PIDs to JSON file.

        Args:
            file_path: Path to JSON file (uses config_path if not specified)
        """
        path = file_path or self.config_path

        if not path:
            return

        # Convert PIDs to serializable format
        pids_data = []

        for (mode, pid_num), pid_def in self.custom_pids.items():
            pid_dict = {
                'mode': mode,
                'pid': pid_num,
                'name': pid_def.name,
                'description': pid_def.description,
                'unit': pid_def.unit,
                'formula': self._decoder_to_formula(pid_def.decoder),
                'num_bytes': pid_def.num_bytes,
                'min_val': pid_def.min_val,
                'max_val': pid_def.max_val
            }
            pids_data.append(pid_dict)

        data = {'pids': pids_data}

        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving custom PIDs: {str(e)}")

    def add_pid(self, mode: int, pid_def: PIDDefinition):
        """
        Add a custom PID definition.

        Args:
            mode: OBD mode number
            pid_def: PID definition
        """
        key = (mode, pid_def.pid)
        self.custom_pids[key] = pid_def

    def remove_pid(self, mode: int, pid: int):
        """
        Remove a custom PID.

        Args:
            mode: OBD mode number
            pid: PID number
        """
        key = (mode, pid)
        if key in self.custom_pids:
            del self.custom_pids[key]

    def get_pid(self, mode: int, pid: int) -> PIDDefinition:
        """
        Get custom PID definition.

        Args:
            mode: OBD mode number
            pid: PID number

        Returns:
            PID definition or None.
        """
        key = (mode, pid)
        return self.custom_pids.get(key)

    def get_all_pids(self) -> List[PIDDefinition]:
        """
        Get all custom PIDs.

        Returns:
            List of PID definitions.
        """
        return list(self.custom_pids.values())

    def _add_pid_from_dict(self, pid_data: Dict):
        """
        Create PID definition from dictionary.

        Args:
            pid_data: Dictionary with PID data
        """
        mode = pid_data.get('mode', 1)
        pid = pid_data['pid']
        name = pid_data['name']
        description = pid_data.get('description', name)
        unit = pid_data.get('unit', '')
        formula = pid_data.get('formula', 'A')
        num_bytes = pid_data.get('num_bytes', 1)
        min_val = pid_data.get('min_val', 0)
        max_val = pid_data.get('max_val', 100)

        # Create decoder function from formula
        decoder = self._formula_to_decoder(formula, num_bytes)

        # Create PID definition
        pid_def = PIDDefinition(
            pid=pid,
            name=name,
            description=description,
            unit=unit,
            decoder=decoder,
            num_bytes=num_bytes,
            min_val=min_val,
            max_val=max_val
        )

        self.add_pid(mode, pid_def)

    def _formula_to_decoder(self, formula: str, num_bytes: int) -> Callable[[List[int]], Any]:
        """
        Convert formula string to decoder function.

        Args:
            formula: Formula string (e.g., "A", "A*256+B", "(A-40)")
            num_bytes: Number of bytes

        Returns:
            Decoder function.
        """
        # Replace A, B, C, D with data[0], data[1], etc.
        formula_eval = formula.replace('A', 'data[0]')

        if num_bytes >= 2:
            formula_eval = formula_eval.replace('B', 'data[1]')
        if num_bytes >= 3:
            formula_eval = formula_eval.replace('C', 'data[2]')
        if num_bytes >= 4:
            formula_eval = formula_eval.replace('D', 'data[3]')

        def decoder(data: List[int]) -> Any:
            try:
                # Evaluate formula
                result = eval(formula_eval)
                return result
            except Exception:
                # Return raw bytes if formula fails
                return ' '.join([f'{b:02X}' for b in data])

        return decoder

    def _decoder_to_formula(self, decoder: Callable) -> str:
        """
        Convert decoder function back to formula string (if possible).

        Args:
            decoder: Decoder function

        Returns:
            Formula string (or 'custom' if cannot determine)
        """
        # This is a simplified reverse mapping
        # In practice, we'd need to store the original formula
        return 'custom'
