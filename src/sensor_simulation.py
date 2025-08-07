import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

class WaterSensorSimulator:
    def __init__(self, db_path='data/water_monitoring.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                timestamp DATETIME PRIMARY KEY,
                temperature FLOAT,
                ph FLOAT,
                turbidity FLOAT,
                dissolved_oxygen FLOAT,
                conductivity FLOAT
            )
        ''')
        conn.commit()
        conn.close()

    def generate_reading(self):
        """Generate a single sensor reading with realistic variations"""
        return {
            'temperature': np.random.normal(25, 2),  # °C
            'ph': np.random.normal(7.5, 0.5),  # pH scale
            'turbidity': np.random.normal(5, 1),  # NTU
            'dissolved_oxygen': np.random.normal(8, 1),  # mg/L
            'conductivity': np.random.normal(500, 50)  # µS/cm
        }

    def simulate_batch(self, duration_hours=24, interval_minutes=5):
        """Simulate sensor readings for a given duration"""
        timestamps = []
        readings = []
        
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=duration_hours)
        current_time = start_time
        
        while current_time <= end_time:
            reading = self.generate_reading()
            readings.append(reading)
            timestamps.append(current_time)
            current_time += timedelta(minutes=interval_minutes)
        
        df = pd.DataFrame(readings, index=timestamps)
        return df

    def save_to_db(self, df):
        """Save simulated data to SQLite database"""
        conn = sqlite3.connect(self.db_path)
        df.to_sql('sensor_data', conn, if_exists='append', index=True, index_label='timestamp')
        conn.close()

if __name__ == '__main__':
    simulator = WaterSensorSimulator()
    data = simulator.simulate_batch()
    simulator.save_to_db(data)
    print("Generated and saved sensor data to database")
