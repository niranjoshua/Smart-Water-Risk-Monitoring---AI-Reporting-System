from typing import List, Optional
import pandas as pd
from datetime import datetime, timedelta
from models.schemas import SensorData, RiskAssessment
from utils.database import DatabaseManager

class WaterRiskPredictor:
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db_manager = db_manager or DatabaseManager()

    def predict_risk(self, data: SensorData) -> RiskAssessment:
        """Predict risk level based on current sensor data"""
        risk_factors = []
        
        # Check temperature
        if data.temperature > 25:
            risk_factors.append("High temperature")
        
        # Check pH
        if data.ph < 6.5 or data.ph > 8.5:
            risk_factors.append("pH out of safe range")
        
        # Check turbidity
        if data.turbidity > 8:
            risk_factors.append("High turbidity")
        
        # Check dissolved oxygen
        if data.dissolved_oxygen < 6:
            risk_factors.append("Low dissolved oxygen")
        
        # Calculate risk level (0-100)
        risk_level = (len(risk_factors) / 4) * 100
        
        return RiskAssessment(
            risk_level=risk_level,
            risk_factors=risk_factors,
            timestamp=datetime.now()
        )
