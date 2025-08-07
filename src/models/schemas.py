from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class SensorData(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    temperature: float = Field(..., ge=0, le=100)
    ph: float = Field(..., ge=0, le=14)
    turbidity: float = Field(..., ge=0)
    dissolved_oxygen: float = Field(..., ge=0, le=20)
    conductivity: float = Field(..., ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-08-07T12:00:00",
                "temperature": 25.5,
                "ph": 7.2,
                "turbidity": 5.0,
                "dissolved_oxygen": 8.5,
                "conductivity": 500
            }
        }

class RiskAssessment(BaseModel):
    risk_level: float = Field(..., ge=0, le=100)
    risk_factors: list[str]
    timestamp: datetime = Field(default_factory=datetime.now)

class Report(BaseModel):
    id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    content: str
    risk_assessment: RiskAssessment
    recommendations: list[str]
