from prometheus_client import Counter, Gauge, Histogram, start_http_server
import time

# Metrics
REQUEST_COUNT = Counter(
    'water_monitoring_requests_total',
    'Total number of requests',
    ['endpoint', 'method', 'status']
)

SENSOR_VALUES = Gauge(
    'water_monitoring_sensor_values',
    'Current sensor readings',
    ['parameter']
)

RESPONSE_TIME = Histogram(
    'water_monitoring_response_time_seconds',
    'Response time in seconds',
    ['endpoint']
)

RISK_LEVEL = Gauge(
    'water_monitoring_risk_level',
    'Current risk level percentage'
)

API_ERRORS = Counter(
    'water_monitoring_api_errors_total',
    'Total number of API errors',
    ['error_type']
)

class MetricsCollector:
    @staticmethod
    def record_request(endpoint: str, method: str, status: int):
        REQUEST_COUNT.labels(endpoint=endpoint, method=method, status=status).inc()

    @staticmethod
    def update_sensor_value(parameter: str, value: float):
        SENSOR_VALUES.labels(parameter=parameter).set(value)

    @staticmethod
    def observe_response_time(endpoint: str, duration: float):
        RESPONSE_TIME.labels(endpoint=endpoint).observe(duration)

    @staticmethod
    def update_risk_level(risk_percentage: float):
        RISK_LEVEL.set(risk_percentage)

    @staticmethod
    def record_error(error_type: str):
        API_ERRORS.labels(error_type=error_type).inc()

def start_metrics_server(port: int = 9090):
    """Start the Prometheus metrics server"""
    start_http_server(port)
    print(f"Metrics server started on port {port}")
