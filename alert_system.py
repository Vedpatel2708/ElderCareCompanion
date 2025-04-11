import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_alerts(health_data, safety_data, reminder_data):
    """Generate alerts based on monitoring data"""
    alerts = []
    
    if health_data is not None:
        health_alerts = generate_health_alerts(health_data)
        alerts.extend(health_alerts)
    
    if safety_data is not None:
        safety_alerts = generate_safety_alerts(safety_data)
        alerts.extend(safety_alerts)
    
    if reminder_data is not None:
        reminder_alerts = generate_reminder_alerts(reminder_data)
        alerts.extend(reminder_alerts)
    
    # Sort alerts by timestamp (most recent first)
    alerts.sort(key=lambda x: x['Timestamp'], reverse=True)
    
    return alerts

def generate_health_alerts(df):
    """Generate alerts from health monitoring data"""
    alerts = []
    
    # Get records where an alert was triggered
    alert_records = df[df['Alert Triggered (Yes/No)'] == 'Yes']
    
    for _, row in alert_records.iterrows():
        device_id = row['Device-ID/User-ID']
        timestamp = row['Timestamp']
        
        # Determine alert type based on abnormal readings
        alert_reasons = []
        if row['Heart Rate Below/Above Threshold (Yes/No)'] == 'Yes':
            alert_reasons.append(f"Abnormal heart rate: {row['Heart Rate']}")
        
        if row['Blood Pressure Below/Above Threshold (Yes/No)'] == 'Yes':
            alert_reasons.append(f"Abnormal blood pressure: {row['Blood Pressure']}")
        
        if row['Glucose Levels Below/Above Threshold (Yes/No)'] == 'Yes':
            alert_reasons.append(f"Abnormal glucose level: {row['Glucose Levels']}")
        
        if row['SpO₂ Below Threshold (Yes/No)'] == 'Yes':
            alert_reasons.append(f"Low oxygen saturation: {row['Oxygen Saturation (SpO₂%)']}%")
        
        message = "; ".join(alert_reasons)
        
        alerts.append({
            'Device-ID': device_id,
            'Alert Type': 'Health',
            'Timestamp': timestamp,
            'Status': 'Active' if row['Caregiver Notified (Yes/No)'] == 'No' else 'Notified',
            'Message': message,
            'Priority': 'High' if len(alert_reasons) > 1 else 'Medium'
        })
    
    return alerts

def generate_safety_alerts(df):
    """Generate alerts from safety monitoring data"""
    alerts = []
    
    # Get records where a fall was detected
    fall_records = df[df['Fall Detected (Yes/No)'] == True]
    
    for _, row in fall_records.iterrows():
        device_id = row['Device-ID/User-ID']
        timestamp = row['Timestamp']
        location = row['Location']
        impact = row['Impact Force Level']
        inactivity = row['Post-Fall Inactivity Duration (Seconds)']
        
        message = f"Fall detected in {location} with {impact} impact. {inactivity} seconds of inactivity."
        
        alerts.append({
            'Device-ID': device_id,
            'Alert Type': 'Fall',
            'Timestamp': timestamp,
            'Status': 'Active' if row['Caregiver Notified (Yes/No)'] == False else 'Notified',
            'Message': message,
            'Priority': 'High' if impact == 'High' or inactivity > 300 else 'Medium'
        })
    
    return alerts

def generate_reminder_alerts(df):
    """Generate alerts for missed reminders"""
    alerts = []
    
    # Get records where a reminder was sent but not acknowledged
    unack_records = df[(df['Reminder Sent (Yes/No)'] == True) & (df['Acknowledged (Yes/No)'] == False)]
    
    for _, row in unack_records.iterrows():
        device_id = row['Device-ID/User-ID']
        timestamp = row['Timestamp']
        reminder_type = row['Reminder Type']
        scheduled_time = row['Scheduled Time']
        
        message = f"{reminder_type} reminder scheduled for {scheduled_time} was not acknowledged."
        
        # Only add alerts for important reminders
        if reminder_type in ['Medication', 'Appointment']:
            alerts.append({
                'Device-ID': device_id,
                'Alert Type': 'Reminder',
                'Timestamp': timestamp,
                'Status': 'Active',
                'Message': message,
                'Priority': 'Medium' if reminder_type == 'Medication' else 'Low'
            })
    
    return alerts

def should_notify_caregiver(alert):
    """Determine if an alert should trigger a caregiver notification"""
    # High priority alerts always notify
    if alert['Priority'] == 'High':
        return True
    
    # Health alerts for vital signs notify
    if alert['Alert Type'] == 'Health' and 'heart rate' in alert['Message'].lower():
        return True
    
    # Fall alerts with medium or high impact notify
    if alert['Alert Type'] == 'Fall' and ('High' in alert['Message'] or 'Medium' in alert['Message']):
        return True
    
    # Medication reminders that are consistently missed
    if alert['Alert Type'] == 'Reminder' and 'Medication' in alert['Message']:
        # Logic for tracking consistent misses would be here
        return False
    
    return False

def notify_caregiver(alert):
    """
    Send notification to caregiver about an alert
    This would integrate with SMS/email/app notification systems
    """
    # In a real system, this would call an API to send notifications
    # For now, we'll just return a message indicating what would be sent
    
    device_id = alert['Device-ID']
    alert_type = alert['Alert Type']
    message = alert['Message']
    timestamp = alert['Timestamp']
    
    notification_message = f"ALERT for {device_id}: {alert_type} - {message} at {timestamp}"
    
    # In reality, this would connect to notification services
    print(f"Notification would be sent: {notification_message}")
    
    # Return success flag
    return True
