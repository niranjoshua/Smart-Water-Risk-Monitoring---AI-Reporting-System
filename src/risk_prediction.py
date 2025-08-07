import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import sqlite3

class WaterRiskPredictor:
    def __init__(self, model_path='models/risk_model.joblib'):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        
    def _get_risk_label(self, row):
        """Define risk conditions based on water parameters"""
        high_risk_conditions = [
            row['temperature'] > 25,  # High temperature risk
            row['ph'] < 6.5 or row['ph'] > 8.5,  # pH out of safe range
            row['turbidity'] > 8,  # High turbidity
            row['dissolved_oxygen'] < 6,  # Low dissolved oxygen
            row['conductivity'] > 600  # High conductivity
        ]
        return 1 if sum(high_risk_conditions) >= 2 else 0

    def prepare_data(self, df):
        """Prepare features and add risk labels"""
        df['risk'] = df.apply(self._get_risk_label, axis=1)
        features = ['temperature', 'ph', 'turbidity', 'dissolved_oxygen', 'conductivity']
        X = df[features]
        y = df['risk']
        return X, y

    def train(self, training_data):
        """Train the risk prediction model"""
        X, y = self.prepare_data(training_data)
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y)
        joblib.dump((self.model, self.scaler), self.model_path)
        
    def load_model(self):
        """Load trained model from disk"""
        self.model, self.scaler = joblib.load(self.model_path)

    def predict(self, data):
        """Predict risk levels for new data"""
        if self.model is None:
            try:
                self.load_model()
            except:
                raise Exception("No trained model found. Please train the model first.")
        
        X_scaled = self.scaler.transform(data[['temperature', 'ph', 'turbidity', 'dissolved_oxygen', 'conductivity']])
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        
        return predictions, probabilities

def train_initial_model():
    """Train initial model with simulated data"""
    from sensor_simulation import WaterSensorSimulator
    
    # Generate training data
    simulator = WaterSensorSimulator()
    training_data = simulator.simulate_batch(duration_hours=168)  # 1 week of data
    
    # Train model
    predictor = WaterRiskPredictor()
    predictor.train(training_data)
    print("Model trained and saved successfully")

if __name__ == '__main__':
    train_initial_model()
