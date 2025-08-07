from dataclasses import dataclass
from typing import Dict
import os

@dataclass
class ProductionConfig:
    # Database settings
    DB_POOL_SIZE: int = 5
    DB_POOL_TIMEOUT: int = 30
    DB_MAX_OVERFLOW: int = 10
    
    # API Rate limits
    API_RATE_LIMIT: int = 60  # requests per minute
    API_TIMEOUT: int = 30     # seconds
    
    # Cache settings
    CACHE_TYPE: str = "redis"
    CACHE_REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_DEFAULT_TIMEOUT: int = 300
    
    # Security
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    PERMANENT_SESSION_LIFETIME: int = 3600  # 1 hour
    
    # Monitoring thresholds
    ALERT_TEMPERATURE_HIGH: float = 30.0
    ALERT_PH_LOW: float = 6.0
    ALERT_PH_HIGH: float = 9.0
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Backup
    BACKUP_ENABLED: bool = True
    BACKUP_INTERVAL_HOURS: int = 24
    BACKUP_RETENTION_DAYS: int = 30
    
    # Health check
    HEALTH_CHECK_INTERVAL: int = 300  # 5 minutes
    
    @classmethod
    def get_alert_thresholds(cls) -> Dict[str, float]:
        return {
            "temperature_high": cls.ALERT_TEMPERATURE_HIGH,
            "ph_low": cls.ALERT_PH_LOW,
            "ph_high": cls.ALERT_PH_HIGH
        }
