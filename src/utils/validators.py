import re
from typing import Dict, Union, List
import numpy as np

class DataValidator:
    # Defines acceptable ranges for water quality parameters
    VALID_RANGES = {
        'temperature': (0, 100),    # °C
        'ph': (0, 14),             # pH scale
        'turbidity': (0, 1000),    # NTU
        'dissolved_oxygen': (0, 20), # mg/L
        'conductivity': (0, 2000)   # µS/cm
    }

    @staticmethod
    def validate_sensor_data(data: Dict[str, float]) -> Dict[str, bool]:
        """
        Validates sensor readings against acceptable ranges
        Returns a dictionary of validation results
        """
        validation_results = {}
        
        for parameter, value in data.items():
            if parameter in DataValidator.VALID_RANGES:
                min_val, max_val = DataValidator.VALID_RANGES[parameter]
                validation_results[parameter] = (
                    isinstance(value, (int, float)) and 
                    not np.isnan(value) and
                    min_val <= value <= max_val
                )
        
        return validation_results

    @staticmethod
    def sanitize_input(value: str) -> str:
        """
        Sanitizes string input to prevent SQL injection
        """
        # Remove any non-alphanumeric characters except underscores and hyphens
        return re.sub(r'[^a-zA-Z0-9_-]', '', str(value))

    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> bool:
        """
        Validates date range format and logic
        """
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        return (bool(date_pattern.match(start_date)) and 
                bool(date_pattern.match(end_date)) and 
                start_date <= end_date)
