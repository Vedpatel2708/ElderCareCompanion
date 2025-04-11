import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Time, Text, MetaData, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

# Get database URL from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create declarative base
Base = declarative_base()

# Define models
class HealthMonitoring(Base):
    __tablename__ = 'health_monitoring'
    
    id = Column(Integer, primary_key=True)
    device_user_id = Column(String(10), index=True)
    timestamp = Column(DateTime)
    heart_rate = Column(Integer)
    heart_rate_threshold = Column(Boolean)
    blood_pressure = Column(String(20))
    blood_pressure_threshold = Column(Boolean)
    systolic = Column(Integer)
    diastolic = Column(Integer)
    glucose_levels = Column(Integer)
    glucose_threshold = Column(Boolean)
    oxygen_saturation = Column(Integer)
    oxygen_threshold = Column(Boolean)
    alert_triggered = Column(Boolean)
    caregiver_notified = Column(Boolean)

    def to_dict(self):
        return {
            'id': self.id,
            'device_user_id': self.device_user_id,
            'timestamp': self.timestamp,
            'heart_rate': self.heart_rate,
            'heart_rate_threshold': self.heart_rate_threshold,
            'blood_pressure': self.blood_pressure,
            'blood_pressure_threshold': self.blood_pressure_threshold,
            'systolic': self.systolic,
            'diastolic': self.diastolic,
            'glucose_levels': self.glucose_levels,
            'glucose_threshold': self.glucose_threshold,
            'oxygen_saturation': self.oxygen_saturation,
            'oxygen_threshold': self.oxygen_threshold,
            'alert_triggered': self.alert_triggered,
            'caregiver_notified': self.caregiver_notified
        }

class SafetyMonitoring(Base):
    __tablename__ = 'safety_monitoring'
    
    id = Column(Integer, primary_key=True)
    device_user_id = Column(String(10), index=True)
    timestamp = Column(DateTime)
    movement_activity = Column(String(50))
    fall_detected = Column(Boolean)
    impact_force_level = Column(String(20))
    post_fall_inactivity_duration = Column(Integer)
    location = Column(String(50))
    alert_triggered = Column(Boolean)
    caregiver_notified = Column(Boolean)

    def to_dict(self):
        return {
            'id': self.id,
            'device_user_id': self.device_user_id,
            'timestamp': self.timestamp,
            'movement_activity': self.movement_activity,
            'fall_detected': self.fall_detected,
            'impact_force_level': self.impact_force_level,
            'post_fall_inactivity_duration': self.post_fall_inactivity_duration,
            'location': self.location,
            'alert_triggered': self.alert_triggered,
            'caregiver_notified': self.caregiver_notified
        }

class DailyReminder(Base):
    __tablename__ = 'daily_reminder'
    
    id = Column(Integer, primary_key=True)
    device_user_id = Column(String(10), index=True)
    timestamp = Column(DateTime)
    reminder_type = Column(String(50))
    scheduled_time = Column(Time)
    reminder_sent = Column(Boolean)
    acknowledged = Column(Boolean)

    def to_dict(self):
        return {
            'id': self.id,
            'device_user_id': self.device_user_id,
            'timestamp': self.timestamp,
            'reminder_type': self.reminder_type,
            'scheduled_time': self.scheduled_time,
            'reminder_sent': self.reminder_sent,
            'acknowledged': self.acknowledged
        }

class Alert(Base):
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    device_user_id = Column(String(10), index=True)
    alert_type = Column(String(50))
    timestamp = Column(DateTime)
    status = Column(String(20))
    message = Column(Text)
    priority = Column(String(20))
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_user_id': self.device_user_id,
            'alert_type': self.alert_type,
            'timestamp': self.timestamp,
            'status': self.status,
            'message': self.message,
            'priority': self.priority
        }

# Create tables
def init_db():
    Base.metadata.create_all(engine)

# Session factory
Session = sessionmaker(bind=engine)

# Import data from CSV to database
def import_csv_to_db():
    try:
        # Function to process data in batches
        def process_in_batches(df, create_record_func, batch_size=50):
            session = Session()
            try:
                for start_idx in range(0, len(df), batch_size):
                    end_idx = min(start_idx + batch_size, len(df))
                    batch = df.iloc[start_idx:end_idx]
                    
                    for _, row in batch.iterrows():
                        record = create_record_func(row)
                        session.add(record)
                    
                    # Commit each batch
                    session.commit()
                    print(f"Imported records {start_idx} to {end_idx}")
            except Exception as e:
                session.rollback()
                print(f"Error in batch processing: {e}")
                raise
            finally:
                session.close()
        
        # Import health monitoring data
        print("Processing health monitoring data...")
        health_data = pd.read_csv('attached_assets/health_monitoring.csv')
        health_data['Timestamp'] = pd.to_datetime(health_data['Timestamp'])
        
        # Extract systolic and diastolic BP
        health_data[['Systolic', 'Diastolic']] = health_data['Blood Pressure'].str.extract(r'(\d+)/(\d+)')
        health_data[['Systolic', 'Diastolic']] = health_data[['Systolic', 'Diastolic']].astype(int)
        
        # Convert Yes/No to boolean
        for col in ['Heart Rate Below/Above Threshold (Yes/No)', 'Blood Pressure Below/Above Threshold (Yes/No)', 
                   'Glucose Levels Below/Above Threshold (Yes/No)', 'SpO₂ Below Threshold (Yes/No)', 
                   'Alert Triggered (Yes/No)', 'Caregiver Notified (Yes/No)']:
            health_data[col] = health_data[col].map({'Yes': True, 'No': False})
        
        # Define health record creation function
        def create_health_record(row):
            return HealthMonitoring(
                device_user_id=row['Device-ID/User-ID'],
                timestamp=row['Timestamp'],
                heart_rate=row['Heart Rate'],
                heart_rate_threshold=row['Heart Rate Below/Above Threshold (Yes/No)'],
                blood_pressure=row['Blood Pressure'],
                blood_pressure_threshold=row['Blood Pressure Below/Above Threshold (Yes/No)'],
                systolic=row['Systolic'],
                diastolic=row['Diastolic'],
                glucose_levels=row['Glucose Levels'],
                glucose_threshold=row['Glucose Levels Below/Above Threshold (Yes/No)'],
                oxygen_saturation=row['Oxygen Saturation (SpO₂%)'],
                oxygen_threshold=row['SpO₂ Below Threshold (Yes/No)'],
                alert_triggered=row['Alert Triggered (Yes/No)'],
                caregiver_notified=row['Caregiver Notified (Yes/No)']
            )
        
        # Process health data in batches
        process_in_batches(health_data, create_health_record)
        
        # Import safety monitoring data
        print("Processing safety monitoring data...")
        safety_data = pd.read_csv('attached_assets/safety_monitoring.csv')
        safety_data['Timestamp'] = pd.to_datetime(safety_data['Timestamp'])
        
        # Convert Yes/No to boolean
        for col in ['Fall Detected (Yes/No)', 'Alert Triggered (Yes/No)', 'Caregiver Notified (Yes/No)']:
            safety_data[col] = safety_data[col].map({'Yes': True, 'No': False})
        
        # Fill missing values
        safety_data['Post-Fall Inactivity Duration (Seconds)'] = safety_data['Post-Fall Inactivity Duration (Seconds)'].fillna(0)
        safety_data['Impact Force Level'] = safety_data['Impact Force Level'].fillna('')
        
        # Define safety record creation function
        def create_safety_record(row):
            return SafetyMonitoring(
                device_user_id=row['Device-ID/User-ID'],
                timestamp=row['Timestamp'],
                movement_activity=row['Movement Activity'],
                fall_detected=row['Fall Detected (Yes/No)'],
                impact_force_level=row['Impact Force Level'] if pd.notna(row['Impact Force Level']) else '',
                post_fall_inactivity_duration=int(row['Post-Fall Inactivity Duration (Seconds)']) if pd.notna(row['Post-Fall Inactivity Duration (Seconds)']) else 0,
                location=row['Location'],
                alert_triggered=row['Alert Triggered (Yes/No)'],
                caregiver_notified=row['Caregiver Notified (Yes/No)']
            )
        
        # Process safety data in batches
        process_in_batches(safety_data, create_safety_record)
        
        # Import reminder data
        print("Processing reminder data...")
        reminder_data = pd.read_csv('attached_assets/daily_reminder.csv')
        reminder_data['Timestamp'] = pd.to_datetime(reminder_data['Timestamp'])
        
        # Convert scheduled time to time
        reminder_data['Scheduled Time'] = pd.to_datetime(reminder_data['Scheduled Time'], format='%H:%M:%S').dt.time
        
        # Convert Yes/No to boolean
        for col in ['Reminder Sent (Yes/No)', 'Acknowledged (Yes/No)']:
            reminder_data[col] = reminder_data[col].map({'Yes': True, 'No': False})
        
        # Define reminder record creation function
        def create_reminder_record(row):
            return DailyReminder(
                device_user_id=row['Device-ID/User-ID'],
                timestamp=row['Timestamp'],
                reminder_type=row['Reminder Type'],
                scheduled_time=row['Scheduled Time'],
                reminder_sent=row['Reminder Sent (Yes/No)'],
                acknowledged=row['Acknowledged (Yes/No)']
            )
        
        # Process reminder data in batches
        process_in_batches(reminder_data, create_reminder_record)
        
        print("Data import completed successfully")
        return True
    except Exception as e:
        print(f"Error importing data: {e}")
        return False

# Retrieve data from database
def get_health_data():
    session = Session()
    health_records = session.query(HealthMonitoring).all()
    
    data = {
        'Device-ID/User-ID': [],
        'Timestamp': [],
        'Heart Rate': [],
        'Heart Rate Below/Above Threshold (Yes/No)': [],
        'Blood Pressure': [],
        'Blood Pressure Below/Above Threshold (Yes/No)': [],
        'Systolic': [],
        'Diastolic': [],
        'Glucose Levels': [],
        'Glucose Levels Below/Above Threshold (Yes/No)': [],
        'Oxygen Saturation (SpO₂%)': [],
        'SpO₂ Below Threshold (Yes/No)': [],
        'Alert Triggered (Yes/No)': [],
        'Caregiver Notified (Yes/No)': []
    }
    
    for record in health_records:
        data['Device-ID/User-ID'].append(record.device_user_id)
        data['Timestamp'].append(record.timestamp)
        data['Heart Rate'].append(record.heart_rate)
        data['Heart Rate Below/Above Threshold (Yes/No)'].append(record.heart_rate_threshold)
        data['Blood Pressure'].append(record.blood_pressure)
        data['Blood Pressure Below/Above Threshold (Yes/No)'].append(record.blood_pressure_threshold)
        data['Systolic'].append(record.systolic)
        data['Diastolic'].append(record.diastolic)
        data['Glucose Levels'].append(record.glucose_levels)
        data['Glucose Levels Below/Above Threshold (Yes/No)'].append(record.glucose_threshold)
        data['Oxygen Saturation (SpO₂%)'].append(record.oxygen_saturation)
        data['SpO₂ Below Threshold (Yes/No)'].append(record.oxygen_threshold)
        data['Alert Triggered (Yes/No)'].append(record.alert_triggered)
        data['Caregiver Notified (Yes/No)'].append(record.caregiver_notified)
    
    session.close()
    return pd.DataFrame(data)

def get_safety_data():
    session = Session()
    safety_records = session.query(SafetyMonitoring).all()
    
    data = {
        'Device-ID/User-ID': [],
        'Timestamp': [],
        'Movement Activity': [],
        'Fall Detected (Yes/No)': [],
        'Impact Force Level': [],
        'Post-Fall Inactivity Duration (Seconds)': [],
        'Location': [],
        'Alert Triggered (Yes/No)': [],
        'Caregiver Notified (Yes/No)': []
    }
    
    for record in safety_records:
        data['Device-ID/User-ID'].append(record.device_user_id)
        data['Timestamp'].append(record.timestamp)
        data['Movement Activity'].append(record.movement_activity)
        data['Fall Detected (Yes/No)'].append(record.fall_detected)
        data['Impact Force Level'].append(record.impact_force_level)
        data['Post-Fall Inactivity Duration (Seconds)'].append(record.post_fall_inactivity_duration)
        data['Location'].append(record.location)
        data['Alert Triggered (Yes/No)'].append(record.alert_triggered)
        data['Caregiver Notified (Yes/No)'].append(record.caregiver_notified)
    
    session.close()
    return pd.DataFrame(data)

def get_reminder_data():
    session = Session()
    reminder_records = session.query(DailyReminder).all()
    
    data = {
        'Device-ID/User-ID': [],
        'Timestamp': [],
        'Reminder Type': [],
        'Scheduled Time': [],
        'Reminder Sent (Yes/No)': [],
        'Acknowledged (Yes/No)': []
    }
    
    for record in reminder_records:
        data['Device-ID/User-ID'].append(record.device_user_id)
        data['Timestamp'].append(record.timestamp)
        data['Reminder Type'].append(record.reminder_type)
        data['Scheduled Time'].append(record.scheduled_time)
        data['Reminder Sent (Yes/No)'].append(record.reminder_sent)
        data['Acknowledged (Yes/No)'].append(record.acknowledged)
    
    session.close()
    return pd.DataFrame(data)

def save_alert(device_id, alert_type, timestamp, status, message, priority):
    session = Session()
    alert = Alert(
        device_user_id=device_id,
        alert_type=alert_type,
        timestamp=timestamp,
        status=status,
        message=message,
        priority=priority
    )
    session.add(alert)
    session.commit()
    session.close()
    return True

def get_alerts():
    session = Session()
    alert_records = session.query(Alert).all()
    
    alerts = []
    for record in alert_records:
        alerts.append({
            'Device-ID': record.device_user_id,
            'Alert Type': record.alert_type,
            'Timestamp': record.timestamp,
            'Status': record.status,
            'Message': record.message,
            'Priority': record.priority
        })
    
    session.close()
    return alerts

def update_alert_status(alert_id, new_status):
    session = Session()
    alert = session.query(Alert).filter_by(id=alert_id).first()
    if alert:
        alert.status = new_status
        session.commit()
        success = True
    else:
        success = False
    session.close()
    return success

# Check if tables exist, otherwise initialize and import data
def setup_database():
    from sqlalchemy import inspect
    inspector = inspect(engine)
    if not inspector.has_table('health_monitoring'):
        print("Initializing database...")
        init_db()
        print("Importing data from CSV files...")
        import_csv_to_db()
        print("Database setup complete.")
    else:
        print("Database already set up.")