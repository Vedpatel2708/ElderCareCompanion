
# Elderly Care Multi-Agent Monitoring System

A comprehensive monitoring and predictive analytics system for elderly care, built with Streamlit. The system uses multiple agents to track health metrics, safety conditions, and medication adherence in real-time.

## Features

### Health Monitoring
- Real-time tracking of vital signs (heart rate, blood pressure, glucose, SpO₂)
- Automated alerts for abnormal health conditions
- Visual analytics of health trends

### Safety Monitoring
- Fall detection and impact analysis
- Movement pattern tracking
- Location-based activity monitoring
- Real-time safety alerts

### Reminder System
- Medication adherence tracking
- Appointment reminders
- Smart scheduling based on effectiveness analysis
- Compliance monitoring

### Predictive Analytics
- Health risk prediction
- Fall risk assessment
- Reminder effectiveness optimization
- AI-powered early warning system

## Tech Stack
- Python
- Streamlit
- SQLAlchemy
- Pandas
- Plotly
- Scikit-learn

## Project Structure
- `app.py`: Main dashboard application
- `pages/`: Individual monitoring modules
  - `health_monitoring.py`: Health metrics tracking
  - `safety_monitoring.py`: Fall detection and movement
  - `reminders.py`: Medication/appointment reminders
  - `predictions.py`: Risk analysis and predictions
- `data_processor.py`: Data processing utilities
- `database.py`: Database operations
- `alert_system.py`: Alert management
- `predictive_models.py`: ML models for risk prediction
- `visualization.py`: Data visualization utilities

## Getting Started
1. Clone the repository
2. Install dependencies
3. Run `streamlit run app.py`


