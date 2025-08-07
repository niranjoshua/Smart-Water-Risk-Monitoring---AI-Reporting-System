import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging
from models.schemas import SensorData
from utils.database import DatabaseManager
from utils.validators import DataValidator

logger = logging.getLogger(__name__)

class SensorSimulationError(Exception):
    """Custom exception for sensor simulation errors"""
    pass

class WaterSensorSimulator:
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db_manager = db_manager or DatabaseManager()
        self.validator = DataValidator()
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database table with proper error handling"""
        try:
            query = '''
                CREATE TABLE IF NOT EXISTS sensor_data (
                    timestamp DATETIME PRIMARY KEY,
                    temperature FLOAT NOT NULL,
                    ph FLOAT NOT NULL,
                    turbidity FLOAT NOT NULL,
                    dissolved_oxygen FLOAT NOT NULL,
                    conductivity FLOAT NOT NULL,
                    CHECK (temperature BETWEEN 0 AND 100),
                    CHECK (ph BETWEEN 0 AND 14),
                    CHECK (turbidity >= 0),
                    CHECK (dissolved_oxygen BETWEEN 0 AND 20),
                    CHECK (conductivity >= 0)
                )
            '''
            self.db_manager.execute_write(query)
            logger.info("Sensor data table initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise SensorSimulationError(f"Database initialization failed: {str(e)}")

    def generate_reading(self) -> Dict[str, float]:
        """Generate a single sensor reading with realistic variations and validation"""
        try:
            reading = {
                'temperature': np.random.normal(25, 2),
                'ph': np.random.normal(7.5, 0.5),
                'turbidity': abs(np.random.normal(5, 1)),  # Always positive
                'dissolved_oxygen': abs(np.random.normal(8, 1)),
                'conductivity': abs(np.random.normal(500, 50))
            }
            
            # Validate the generated data
            validation_results = self.validator.validate_sensor_data(reading)
            if not all(validation_results.values()):
                invalid_params = [k for k, v in validation_results.items() if not v]
                raise SensorSimulationError(f"Invalid sensor readings for: {invalid_params}")
            
            return reading
        except Exception as e:
            logger.error(f"Error generating sensor reading: {str(e)}")
            raise SensorSimulationError(f"Failed to generate sensor reading: {str(e)}")

    def simulate_batch(self, duration_hours: int = 24, interval_minutes: int = 5) -> pd.DataFrame:
        """Simulate sensor readings for a given duration with error handling"""
        try:
            timestamps = []
            readings = []
            
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=duration_hours)
            current_time = start_time
            
            while current_time <= end_time:
                try:
                    reading = self.generate_reading()
                    readings.append(reading)
                    timestamps.append(current_time)
                except SensorSimulationError as e:
                    logger.warning(f"Skipping invalid reading at {current_time}: {str(e)}")
                finally:
                    current_time += timedelta(minutes=interval_minutes)
            
            if not readings:
                raise SensorSimulationError("No valid readings generated")
            
            df = pd.DataFrame(readings, index=timestamps)
            return df
        except Exception as e:
            logger.error(f"Batch simulation failed: {str(e)}")
            raise SensorSimulationError(f"Batch simulation failed: {str(e)}")

    def save_to_db(self, df: pd.DataFrame) -> None:
        """Save simulated data to database with error handling"""
        try:
            # Convert DataFrame to list of SensorData models for validation
            sensor_data_list = []
            for timestamp, row in df.iterrows():
                sensor_data = SensorData(
                    timestamp=timestamp,
                    temperature=row['temperature'],
                    ph=row['ph'],
                    turbidity=row['turbidity'],
                    dissolved_oxygen=row['dissolved_oxygen'],
                    conductivity=row['conductivity']
                )
                sensor_data_list.append(sensor_data)

            # Prepare and execute batch insert
            query = '''
                INSERT INTO sensor_data 
                (timestamp, temperature, ph, turbidity, dissolved_oxygen, conductivity)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            
            data = [(
                data.timestamp,
                data.temperature,
                data.ph,
                data.turbidity,
                data.dissolved_oxygen,
                data.conductivity
            ) for data in sensor_data_list]
            
            for record in data:
                self.db_manager.execute_write(query, record)
                
            logger.info(f"Successfully saved {len(data)} readings to database")
        except Exception as e:
            logger.error(f"Failed to save data to database: {str(e)}")
            raise SensorSimulationError(f"Database save operation failed: {str(e)}")

    def clean_old_data(self, retention_days: int = 30) -> None:
        """Clean up old data beyond retention period"""
        try:
            query = "DELETE FROM sensor_data WHERE timestamp < datetime('now', ?)"
            self.db_manager.execute_write(query, (f'-{retention_days} days',))
            logger.info(f"Cleaned up data older than {retention_days} days")
        except Exception as e:
            logger.error(f"Failed to clean old data: {str(e)}")
            raise SensorSimulationError(f"Data cleanup failed: {str(e)}")
