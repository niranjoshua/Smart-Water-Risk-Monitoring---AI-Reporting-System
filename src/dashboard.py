import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

from sensor_simulation import WaterSensorSimulator
from risk_prediction import WaterRiskPredictor
from report_generator import RiskReportGenerator

class WaterMonitoringDashboard:
    def __init__(self):
        self.simulator = WaterSensorSimulator()
        self.predictor = WaterRiskPredictor()
        self.report_generator = RiskReportGenerator()

    def load_recent_data(self):
        """Load recent sensor data from database"""
        conn = sqlite3.connect('data/water_monitoring.db')
        df = pd.read_sql_query("""
            SELECT * FROM sensor_data 
            WHERE timestamp >= datetime('now', '-24 hours')
            ORDER BY timestamp DESC
        """, conn)
        conn.close()
        return df

    def create_line_plot(self, df, parameter):
        """Create a line plot for a specific parameter"""
        fig = px.line(df, x='timestamp', y=parameter, 
                     title=f'{parameter.replace("_", " ").title()} Over Time')
        return fig

    def create_gauge_chart(self, value, title, min_val, max_val, safe_range):
        """Create a gauge chart for current readings"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': title},
            gauge={
                'axis': {'range': [min_val, max_val]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': safe_range, 'color': "lightgreen"},
                ],
            }
        ))
        return fig

    def run_dashboard(self):
        st.title("Smart Water Risk Monitoring System")
        
        # Sidebar for controls
        st.sidebar.title("Controls")
        if st.sidebar.button("Simulate New Data"):
            data = self.simulator.simulate_batch(duration_hours=1)
            self.simulator.save_to_db(data)
            st.sidebar.success("New data generated!")

        # Load and display current data
        df = self.load_recent_data()
        if df.empty:
            st.warning("No data available. Please simulate some data first.")
            return

        # Latest Readings Section
        st.header("Current Readings")
        latest = df.iloc[0]
        col1, col2, col3 = st.columns(3)

        with col1:
            st.plotly_chart(self.create_gauge_chart(
                latest['temperature'], "Temperature (°C)", 
                0, 40, [20, 25]
            ), use_container_width=True)

        with col2:
            st.plotly_chart(self.create_gauge_chart(
                latest['ph'], "pH Level",
                0, 14, [6.5, 8.5]
            ), use_container_width=True)

        with col3:
            st.plotly_chart(self.create_gauge_chart(
                latest['turbidity'], "Turbidity (NTU)",
                0, 20, [0, 8]
            ), use_container_width=True)

        # Trends Section
        st.header("Trends")
        parameter = st.selectbox(
            "Select Parameter to View",
            ['temperature', 'ph', 'turbidity', 'dissolved_oxygen', 'conductivity']
        )
        st.plotly_chart(self.create_line_plot(df, parameter))

        # Risk Assessment Section
        st.header("Risk Assessment")
        predictions, probabilities = self.predictor.predict(df)
        risk_percentage = (predictions.sum() / len(predictions)) * 100

        st.metric(
            "Current Risk Level",
            f"{risk_percentage:.1f}%",
            "Based on last 24 hours"
        )

        # AI-Generated Report Section
        st.header("AI Risk Report")
        if st.button("Generate New Report"):
            with st.spinner("Generating report..."):
                report = self.report_generator.generate_report()
                st.text_area("Report", report, height=300)

if __name__ == "__main__":
    dashboard = WaterMonitoringDashboard()
    dashboard.run_dashboard()
