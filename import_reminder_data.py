import database
import pandas as pd
from sqlalchemy import inspect

def import_reminder_data_only():
    print("Processing reminder data...")
    reminder_data = pd.read_csv('attached_assets/daily_reminder.csv')
    reminder_data['Timestamp'] = pd.to_datetime(reminder_data['Timestamp'])
    
    # Convert scheduled time to time
    reminder_data['Scheduled Time'] = pd.to_datetime(reminder_data['Scheduled Time'], format='%H:%M:%S').dt.time
    
    # Convert Yes/No to boolean
    for col in ['Reminder Sent (Yes/No)', 'Acknowledged (Yes/No)']:
        reminder_data[col] = reminder_data[col].map({'Yes': True, 'No': False})
    
    # Function to process data in batches
    def process_in_batches(df, batch_size=50):
        session = database.Session()
        try:
            for start_idx in range(0, len(df), batch_size):
                end_idx = min(start_idx + batch_size, len(df))
                batch = df.iloc[start_idx:end_idx]
                
                for _, row in batch.iterrows():
                    reminder_record = database.DailyReminder(
                        device_user_id=row['Device-ID/User-ID'],
                        timestamp=row['Timestamp'],
                        reminder_type=row['Reminder Type'],
                        scheduled_time=row['Scheduled Time'],
                        reminder_sent=row['Reminder Sent (Yes/No)'],
                        acknowledged=row['Acknowledged (Yes/No)']
                    )
                    session.add(reminder_record)
                
                # Commit each batch
                session.commit()
                print(f"Imported reminder records {start_idx} to {end_idx}")
        except Exception as e:
            session.rollback()
            print(f"Error in batch processing: {e}")
            raise
        finally:
            session.close()
    
    # Process reminder data in batches
    process_in_batches(reminder_data)

if __name__ == "__main__":
    # Make sure tables exist
    inspector = inspect(database.engine)
    if not inspector.has_table('daily_reminder'):
        database.init_db()
    
    # Import reminder data
    print("Starting reminder data import process...")
    import_reminder_data_only()
    print("Reminder data import process completed.")