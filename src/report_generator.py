import os
from datetime import datetime, timedelta
import pandas as pd
from langchain_community.llms import OpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from utils.database import DatabaseManager
from utils.validators import DataValidator
from utils.api_security import require_api_key, openai_rate_limiter

load_dotenv()  # Load OpenAI API key from .env file

class RiskReportGenerator:
    def __init__(self, db_path='data/water_monitoring.db'):
        self.db_manager = DatabaseManager(db_path)
        self.llm = OpenAI(temperature=0.7)
        
        self.report_template = PromptTemplate(
            input_variables=["date", "metrics", "risk_levels", "historical_context"],
            template="""
            Water Quality Risk Report - {date}

            Based on the analysis of today's water quality metrics:
            {metrics}

            Risk Assessment:
            {risk_levels}

            Historical Context and Trends:
            {historical_context}

            Please provide:
            1. A summary of current water quality status
            2. Key risk factors identified
            3. Recommended preventive actions
            4. Trends comparison with historical data
            5. Priority areas for monitoring
            """
        )

    def get_recent_data(self, hours=24):
        """Fetch recent sensor data from database"""
        query = """
            SELECT * FROM sensor_data 
            WHERE timestamp >= datetime('now', ?)
            ORDER BY timestamp DESC
        """
        with self.db_manager.get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=(f'-{hours} hours',))
        return df

    def get_historical_context(self, days=7):
        """Get statistical summary of historical data"""
        query = """
            SELECT 
                avg(temperature) as avg_temp,
                avg(ph) as avg_ph,
                avg(turbidity) as avg_turbidity,
                avg(dissolved_oxygen) as avg_do,
                avg(conductivity) as avg_conductivity
            FROM sensor_data 
            WHERE timestamp >= datetime('now', ?)
        """
        with self.db_manager.get_connection() as conn:
            historical_stats = pd.read_sql_query(query, conn, params=(f'-{days} days',))
        return historical_stats

    def format_metrics(self, df):
        """Format current metrics for the report"""
        latest = df.iloc[0]
        return f"""
        Temperature: {latest['temperature']:.1f}°C
        pH: {latest['ph']:.1f}
        Turbidity: {latest['turbidity']:.1f} NTU
        Dissolved Oxygen: {latest['dissolved_oxygen']:.1f} mg/L
        Conductivity: {latest['conductivity']:.1f} µS/cm
        """

    def generate_report(self):
        """Generate a comprehensive risk report"""
        current_data = self.get_recent_data()
        historical_stats = self.get_historical_context()
        
        # Get risk predictions
        from risk_prediction import WaterRiskPredictor
        predictor = WaterRiskPredictor()
        predictions, probabilities = predictor.predict(current_data)
        risk_percentage = (predictions.sum() / len(predictions)) * 100
        
        report_input = self.report_template.format(
            date=datetime.now().strftime("%Y-%m-%d"),
            metrics=self.format_metrics(current_data),
            risk_levels=f"Overall Risk Level: {risk_percentage:.1f}% of readings show elevated risk",
            historical_context=f"Weekly Averages: Temp={historical_stats['avg_temp'].iloc[0]:.1f}°C, pH={historical_stats['avg_ph'].iloc[0]:.1f}"
        )
        
        return self.llm.predict(report_input)

if __name__ == '__main__':
    generator = RiskReportGenerator()
    report = generator.generate_report()
    print(report)
