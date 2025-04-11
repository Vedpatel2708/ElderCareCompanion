import database
import pandas as pd
from sqlalchemy import inspect

def import_safety_data_only():
    print("Processing safety monitoring data...")
    safety_data = pd.read_csv('attached_assets/safety_monitoring.csv')
    safety_data['Timestamp'] = pd.to_datetime(safety_data['Timestamp'])
    
    # Convert Yes/No to boolean
    for col in ['Fall Detected (Yes/No)', 'Alert Triggered (Yes/No)', 'Caregiver Notified (Yes/No)']:
        safety_data[col] = safety_data[col].map({'Yes': True, 'No': False})
    
    # Fill missing values
    safety_data['Post-Fall Inactivity Duration (Seconds)'] = safety_data['Post-Fall Inactivity Duration (Seconds)'].fillna(0)
    safety_data['Impact Force Level'] = safety_data['Impact Force Level'].fillna('')
    
    # Function to process data in batches
    def process_in_batches(df, batch_size=50):
        session = database.Session()
        try:
            for start_idx in range(0, len(df), batch_size):
                end_idx = min(start_idx + batch_size, len(df))
                batch = df.iloc[start_idx:end_idx]
                
                for _, row in batch.iterrows():
                    safety_record = database.SafetyMonitoring(
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
                    session.add(safety_record)
                
                # Commit each batch
                session.commit()
                print(f"Imported safety records {start_idx} to {end_idx}")
        except Exception as e:
            session.rollback()
            print(f"Error in batch processing: {e}")
            raise
        finally:
            session.close()
    
    # Process safety data in batches
    process_in_batches(safety_data)

if __name__ == "__main__":
    # Make sure tables exist
    inspector = inspect(database.engine)
    if not inspector.has_table('safety_monitoring'):
        database.init_db()
    
    # Import safety data
    print("Starting safety data import process...")
    import_safety_data_only()
    print("Safety data import process completed.")