from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import uvicorn
from typing import List
import logging

from auth.security import (
    Token, User, authenticate_user, create_access_token,
    get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from utils.error_handlers import setup_exception_handlers
from middleware.base import setup_middleware
from utils.logger import Logger
from utils.database import DatabaseManager
from utils.logger import Logger
from models.schemas import SensorData
from services.sensor_simulation import WaterSensorSimulator
from services.risk_prediction import WaterRiskPredictor

# Initialize FastAPI app
app = FastAPI(
    title="Smart Water Monitoring System",
    description="API for water quality monitoring and risk assessment",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db = DatabaseManager()
logger = Logger().get_logger()
sensor_simulator = WaterSensorSimulator(db)
risk_predictor = WaterRiskPredictor(db)

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/sensor-data/current", response_model=SensorData)
async def get_current_readings(current_user: User = Depends(get_current_active_user)):
    """Get current sensor readings"""
    try:
        latest_reading = sensor_simulator.generate_reading()
        return SensorData(
            timestamp=datetime.now(),
            **latest_reading
        )
    except Exception as e:
        logger.error(f"Error getting current readings: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/sensor-data/history", response_model=List[SensorData])
async def get_historical_data(
    hours: int = 24,
    current_user: User = Depends(get_current_active_user)
):
    """Get historical sensor data"""
    try:
        df = sensor_simulator.simulate_batch(duration_hours=hours)
        return [SensorData(timestamp=ts, **row.to_dict()) 
                for ts, row in df.iterrows()]
    except Exception as e:
        logger.error(f"Error getting historical data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/reports/generate")
async def generate_report(current_user: User = Depends(get_current_active_user)):
    """Generate a new risk report"""
    try:
        current_data = await get_current_readings(current_user)
        risk_assessment = risk_predictor.predict_risk(current_data)
        return {
            "risk_assessment": risk_assessment,
            "timestamp": datetime.now(),
            "recommendations": [
                f"Address {factor.lower()}" for factor in risk_assessment.risk_factors
            ] if risk_assessment.risk_factors else ["All parameters within safe range"]
        }
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
