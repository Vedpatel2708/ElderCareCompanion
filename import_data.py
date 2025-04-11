import database

if __name__ == "__main__":
    print("Starting data import process...")
    # Make sure tables exist
    database.init_db()
    # Import data
    database.import_csv_to_db()
    print("Data import process completed.")