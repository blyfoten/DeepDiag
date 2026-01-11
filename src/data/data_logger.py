"""
Data logging functionality for recording OBD sessions to CSV.
"""

import csv
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path


class DataLogger:
    """Logger for recording OBD data to CSV files."""

    def __init__(self, log_dir: str = 'logs'):
        """
        Initialize data logger.

        Args:
            log_dir: Directory for log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        self.current_file = None
        self.csv_writer = None
        self.file_handle = None
        self.columns = []
        self.logging = False

    def start_logging(self, columns: List[str], filename: str = None):
        """
        Start logging session.

        Args:
            columns: List of column names (PIDs to log)
            filename: Optional filename (auto-generated if not provided)
        """
        if self.logging:
            self.stop_logging()

        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'obd_log_{timestamp}.csv'

        self.current_file = self.log_dir / filename
        self.columns = ['timestamp'] + columns

        # Open file and create CSV writer
        self.file_handle = open(self.current_file, 'w', newline='')
        self.csv_writer = csv.DictWriter(self.file_handle, fieldnames=self.columns)
        self.csv_writer.writeheader()

        self.logging = True

    def log_data(self, data: Dict[str, Any]):
        """
        Log a data point.

        Args:
            data: Dictionary mapping column names to values
        """
        if not self.logging:
            return

        # Add timestamp
        row = {
            'timestamp': datetime.now().isoformat()
        }

        # Add data values
        for col in self.columns[1:]:  # Skip timestamp column
            row[col] = data.get(col, '')

        # Write row
        try:
            self.csv_writer.writerow(row)
            self.file_handle.flush()  # Ensure data is written immediately
        except Exception as e:
            print(f"Error writing log data: {str(e)}")

    def stop_logging(self):
        """Stop logging and close file."""
        if not self.logging:
            return

        if self.file_handle:
            self.file_handle.close()

        self.logging = False
        self.current_file = None
        self.csv_writer = None
        self.file_handle = None

    def is_logging(self) -> bool:
        """Check if currently logging."""
        return self.logging

    def get_current_file(self) -> str:
        """Get path to current log file."""
        if self.current_file:
            return str(self.current_file)
        return None

    def get_log_files(self) -> List[str]:
        """
        Get list of all log files.

        Returns:
            List of log file paths.
        """
        log_files = list(self.log_dir.glob('*.csv'))
        return [str(f) for f in sorted(log_files, reverse=True)]

    def export_to_csv(self, data_points: List[Dict[str, Any]], filename: str, columns: List[str]):
        """
        Export data points to a CSV file.

        Args:
            data_points: List of data dictionaries
            filename: Output filename
            columns: Column names
        """
        filepath = self.log_dir / filename

        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()
                writer.writerows(data_points)
        except Exception as e:
            print(f"Error exporting to CSV: {str(e)}")

    def __del__(self):
        """Cleanup on deletion."""
        if self.logging:
            self.stop_logging()
