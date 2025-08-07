# Smart Water Risk Monitoring & AI Reporting System

A comprehensive IoT water monitoring system that predicts risk conditions for legionella formation and provides AI-generated risk reports with actionable insights.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🌊 **Real-time Water Quality Monitoring**
  - Temperature, pH, turbidity tracking
  - Dissolved oxygen monitoring
  - Conductivity measurement

- 🤖 **AI-Powered Risk Assessment**
  - Machine learning-based risk prediction
  - Real-time alerts for dangerous conditions
  - Historical trend analysis

- 📊 **Interactive Dashboard**
  - Real-time data visualization
  - Risk level indicators
  - Historical data trends

- 📝 **Automated Reporting**
  - AI-generated risk reports
  - Actionable recommendations
  - PDF report generation

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/smart-water-monitoring.git
   cd smart-water-monitoring
   ```

2. **Set up environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

4. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

Visit `http://localhost:8000/docs` for the API documentation.

## Project Structure

```
src/
├── api/             # FastAPI endpoints
├── models/          # Data models
├── services/        # Business logic
├── middleware/      # Middleware components
├── utils/          # Utility functions
└── tests/          # Test files
```

## Development

### Prerequisites
- Python 3.10+
- FastAPI
- SQLite
- Redis (optional, for caching)

### Running Tests
```bash
pytest
```

### Code Quality
```bash
# Run linting
flake8 src tests

# Run type checking
mypy src
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgments

- OpenAI for LLM capabilities
- FastAPI for the web framework
- Streamlit for the dashboard interface

## Project Structure

```
Smart Water Monitoring System/
├── data/                  # Database and data files
├── models/               # Trained ML models
├── notebooks/           # Jupyter notebooks for analysis
└── src/                 # Source code
    ├── sensor_simulation.py    # IoT sensor data simulation
    ├── risk_prediction.py      # ML risk prediction model
    ├── report_generator.py     # RAG-powered report generation
    └── dashboard.py           # Streamlit dashboard
```

## Setup Instructions

1. Create a Python virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install required packages:
```bash
pip install numpy pandas scikit-learn streamlit plotly sqlite3 python-dotenv langchain openai
```

3. Configure environment variables:
- Copy `.env.example` to `.env`
- Add your OpenAI API key to `.env`

## Running the System

1. Generate initial sensor data and train the model:
```bash
python src/sensor_simulation.py
python src/risk_prediction.py
```

2. Launch the dashboard:
```bash
streamlit run src/dashboard.py
```

## Features

1. **IoT Sensor Data Simulation**
   - Simulates water quality parameters including temperature, pH, turbidity
   - Stores data in SQLite database
   - Configurable simulation intervals

2. **AI Risk Prediction**
   - Machine learning model to detect high-risk conditions
   - Real-time risk assessment
   - Historical trend analysis

3. **RAG-Powered Risk Reporting**
   - AI-generated daily reports
   - Actionable insights and recommendations
   - Historical context integration

4. **Interactive Dashboard**
   - Real-time monitoring of water parameters
   - Risk level visualization
   - Historical trends and analysis
   - On-demand AI report generation

## Data Sources

The system uses simulated data that mimics real-world water quality parameters:

- Temperature (°C)
- pH levels
- Turbidity (NTU)
- Dissolved Oxygen (mg/L)
- Conductivity (µS/cm)

Risk thresholds are based on standard water quality guidelines for legionella prevention.

## Security & Scalability

The system implements several security best practices:

- Environment variable configuration for sensitive data
- Database access controls
- Input validation and sanitization

For production deployment, consider:

- Implementing user authentication
- Using secure cloud storage
- Setting up automated backups
- Implementing API rate limiting
- Adding data validation layers
