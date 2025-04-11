import pandas as pd
import numpy as np
from datetime import datetime

def process_health_data(df):
    """Process health monitoring data"""
    # Convert timestamp to datetime
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    # Create date column
    df['Date'] = df['Timestamp'].dt.date
    
    # Clean up column names
    df.columns = [col.strip() for col in df.columns]
    
    # Extract systolic and diastolic BP
    df[['Systolic', 'Diastolic']] = df['Blood Pressure'].str.extract(r'(\d+)/(\d+)')
    df[['Systolic', 'Diastolic']] = df[['Systolic', 'Diastolic']].astype(int)
    
    # Clean up SpO₂ column - remove '%' if present
    if 'Oxygen Saturation (SpO₂%)' in df.columns:
        df['SpO₂'] = df['Oxygen Saturation (SpO₂%)'].astype(int)
    
    return df

def process_safety_data(df):
    """Process safety monitoring data"""
    # Convert timestamp to datetime
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    # Create date column
    df['Date'] = df['Timestamp'].dt.date
    
    # Clean up column names
    df.columns = [col.strip() for col in df.columns]
    
    # Fill missing values for inactivity duration
    if 'Post-Fall Inactivity Duration (Seconds)' in df.columns:
        df['Post-Fall Inactivity Duration (Seconds)'] = df['Post-Fall Inactivity Duration (Seconds)'].fillna(0)
    
    # Convert Yes/No columns to boolean
    for col in ['Fall Detected (Yes/No)', 'Alert Triggered (Yes/No)', 'Caregiver Notified (Yes/No)']:
        if col in df.columns:
            df[col] = df[col].map({'Yes': True, 'No': False})
    
    return df

def process_reminder_data(df):
    """Process daily reminder data"""
    # Convert timestamp to datetime
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    # Create date column
    df['Date'] = df['Timestamp'].dt.date
    
    # Clean up column names
    df.columns = [col.strip() for col in df.columns]
    
    # Convert scheduled time to datetime
    df['Scheduled Time'] = pd.to_datetime(df['Scheduled Time'], format='%H:%M:%S').dt.time
    
    # Convert Yes/No columns to boolean
    for col in ['Reminder Sent (Yes/No)', 'Acknowledged (Yes/No)']:
        if col in df.columns:
            df[col] = df[col].map({'Yes': True, 'No': False})
    
    return df

def get_health_stats(df):
    """Calculate health statistics for dashboard"""
    if df is None or len(df) == 0:
        return {
            'abnormal_hr': 0,
            'abnormal_bp': 0,
            'abnormal_glucose': 0,
            'low_spo2': 0
        }
    
    # Calculate percentage of abnormal readings
    try:
        # Handle boolean values
        if df['Heart Rate Below/Above Threshold (Yes/No)'].dtype == bool:
            abnormal_hr = df['Heart Rate Below/Above Threshold (Yes/No)'].mean() * 100
        else:
            abnormal_hr = df['Heart Rate Below/Above Threshold (Yes/No)'].map({'Yes': 1, 'No': 0, True: 1, False: 0}).mean() * 100
        
        if df['Blood Pressure Below/Above Threshold (Yes/No)'].dtype == bool:
            abnormal_bp = df['Blood Pressure Below/Above Threshold (Yes/No)'].mean() * 100
        else:
            abnormal_bp = df['Blood Pressure Below/Above Threshold (Yes/No)'].map({'Yes': 1, 'No': 0, True: 1, False: 0}).mean() * 100
        
        if df['Glucose Levels Below/Above Threshold (Yes/No)'].dtype == bool:
            abnormal_glucose = df['Glucose Levels Below/Above Threshold (Yes/No)'].mean() * 100
        else:
            abnormal_glucose = df['Glucose Levels Below/Above Threshold (Yes/No)'].map({'Yes': 1, 'No': 0, True: 1, False: 0}).mean() * 100
        
        if df['SpO₂ Below Threshold (Yes/No)'].dtype == bool:
            low_spo2 = df['SpO₂ Below Threshold (Yes/No)'].mean() * 100
        else:
            low_spo2 = df['SpO₂ Below Threshold (Yes/No)'].map({'Yes': 1, 'No': 0, True: 1, False: 0}).mean() * 100
    except Exception as e:
        print(f"Error calculating health stats: {e}")
        return {
            'abnormal_hr': 0,
            'abnormal_bp': 0,
            'abnormal_glucose': 0,
            'low_spo2': 0
        }
    
    # Handle NaN values
    return {
        'abnormal_hr': round(abnormal_hr) if not np.isnan(abnormal_hr) else 0,
        'abnormal_bp': round(abnormal_bp) if not np.isnan(abnormal_bp) else 0,
        'abnormal_glucose': round(abnormal_glucose) if not np.isnan(abnormal_glucose) else 0,
        'low_spo2': round(low_spo2) if not np.isnan(low_spo2) else 0
    }

def get_safety_stats(df):
    """Calculate safety statistics for dashboard"""
    if df is None or len(df) == 0:
        return {
            'fall_count': 0,
            'high_impact_falls': 0,
            'avg_inactivity_duration': 0,
            'alerts_triggered': 0
        }
    
    try:
        # Count fall incidents - handle both boolean and Yes/No string values
        if df['Fall Detected (Yes/No)'].dtype == bool:
            fall_count = df['Fall Detected (Yes/No)'].sum()
            # For boolean True/False values
            fall_df = df[df['Fall Detected (Yes/No)'] == True]
        else:
            # For string 'Yes'/'No' values
            fall_count = df['Fall Detected (Yes/No)'].map({'Yes': 1, 'No': 0, True: 1, False: 0}).sum()
            fall_df = df[df['Fall Detected (Yes/No)'].isin(['Yes', True])]
        
        # Count high impact falls
        high_impact_falls = len(fall_df[fall_df['Impact Force Level'] == 'High'])
        
        # Calculate average inactivity duration for falls
        avg_inactivity = fall_df['Post-Fall Inactivity Duration (Seconds)'].mean() if len(fall_df) > 0 else 0
        
        # Count alerts triggered
        if df['Alert Triggered (Yes/No)'].dtype == bool:
            alerts_triggered = df['Alert Triggered (Yes/No)'].sum()
        else:
            alerts_triggered = df['Alert Triggered (Yes/No)'].map({'Yes': 1, 'No': 0, True: 1, False: 0}).sum()
    except Exception as e:
        print(f"Error calculating safety stats: {e}")
        return {
            'fall_count': 0,
            'high_impact_falls': 0,
            'avg_inactivity_duration': 0,
            'alerts_triggered': 0
        }
    
    return {
        'fall_count': int(fall_count) if not np.isnan(fall_count) else 0,
        'high_impact_falls': int(high_impact_falls) if not np.isnan(high_impact_falls) else 0,
        'avg_inactivity_duration': avg_inactivity if not np.isnan(avg_inactivity) else 0,
        'alerts_triggered': int(alerts_triggered) if not np.isnan(alerts_triggered) else 0
    }

def get_reminder_stats(df):
    """Calculate reminder statistics for dashboard"""
    if df is None or len(df) == 0:
        return {
            'medication_count': 0,
            'appointment_count': 0,
            'sent_rate': 0,
            'ack_rate': 0
        }
    
    try:
        # Count reminder types
        medication_count = len(df[df['Reminder Type'] == 'Medication'])
        appointment_count = len(df[df['Reminder Type'] == 'Appointment'])
        
        # Calculate rates - handle both boolean and Yes/No string values
        if df['Reminder Sent (Yes/No)'].dtype == bool:
            sent_rate = df['Reminder Sent (Yes/No)'].mean() * 100
            # For boolean values
            sent_df = df[df['Reminder Sent (Yes/No)'] == True]
        else:
            # For string values
            sent_rate = df['Reminder Sent (Yes/No)'].map({'Yes': 1, 'No': 0, True: 1, False: 0}).mean() * 100
            sent_df = df[df['Reminder Sent (Yes/No)'].isin(['Yes', True])]
        
        # Calculate acknowledgment rate
        if sent_df.empty:
            ack_rate = 0
        else:
            if 'Acknowledged (Yes/No)' in sent_df.columns:
                if sent_df['Acknowledged (Yes/No)'].dtype == bool:
                    ack_rate = sent_df['Acknowledged (Yes/No)'].mean() * 100
                else:
                    ack_rate = sent_df['Acknowledged (Yes/No)'].map({'Yes': 1, 'No': 0, True: 1, False: 0}).mean() * 100
            else:
                ack_rate = 0
    except Exception as e:
        print(f"Error calculating reminder stats: {e}")
        return {
            'medication_count': 0,
            'appointment_count': 0,
            'sent_rate': 0,
            'ack_rate': 0
        }
    
    return {
        'medication_count': int(medication_count) if not np.isnan(medication_count) else 0,
        'appointment_count': int(appointment_count) if not np.isnan(appointment_count) else 0,
        'sent_rate': sent_rate if not np.isnan(sent_rate) else 0,
        'ack_rate': ack_rate if not np.isnan(ack_rate) else 0
    }

def merge_data_for_analysis(health_df, safety_df, reminder_df):
    """Merge datasets for comprehensive analysis"""
    # Prepare common columns and select relevant features
    health_features = health_df[['Device-ID/User-ID', 'Timestamp', 'Heart Rate', 
                                'Systolic', 'Diastolic', 'Glucose Levels', 'SpO₂',
                                'Alert Triggered (Yes/No)']].copy()
    health_features.rename(columns={'Alert Triggered (Yes/No)': 'Health Alert'}, inplace=True)
    
    safety_features = safety_df[['Device-ID/User-ID', 'Timestamp', 'Movement Activity',
                                'Fall Detected (Yes/No)', 'Impact Force Level',
                                'Alert Triggered (Yes/No)']].copy()
    safety_features.rename(columns={'Alert Triggered (Yes/No)': 'Safety Alert'}, inplace=True)
    
    reminder_features = reminder_df[['Device-ID/User-ID', 'Timestamp', 'Reminder Type',
                                    'Reminder Sent (Yes/No)', 'Acknowledged (Yes/No)']].copy()
    
    # Convert timestamps to date for merging
    health_features['Date'] = health_features['Timestamp'].dt.date
    safety_features['Date'] = safety_features['Timestamp'].dt.date
    reminder_features['Date'] = reminder_features['Timestamp'].dt.date
    
    # Merge on device ID and date
    merged_df = pd.merge(
        health_features, 
        safety_features, 
        on=['Device-ID/User-ID', 'Date'], 
        how='outer',
        suffixes=('_health', '_safety')
    )
    
    merged_df = pd.merge(
        merged_df,
        reminder_features,
        on=['Device-ID/User-ID', 'Date'],
        how='outer',
        suffixes=('', '_reminder')
    )
    
    # Create composite features
    merged_df['Has Health Alert'] = merged_df['Health Alert'].fillna(False)
    merged_df['Has Safety Alert'] = merged_df['Safety Alert'].fillna(False)
    merged_df['Has Any Alert'] = merged_df['Has Health Alert'] | merged_df['Has Safety Alert']
    
    return merged_df
