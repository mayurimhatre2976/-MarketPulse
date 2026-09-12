"""
MarketPulse Database Initialization Script
Initializes the database schema for MySQL / XAMPP.
"""
from database.db import init_database_tables

if __name__ == '__main__':
    print("========================================")
    print("MarketPulse Database Initialization")
    print("========================================")
    success = init_database_tables()
    if success:
        print("[SUCCESS] MarketPulse database schema is ready!")
    else:
        print("[ERROR] Failed to initialize database tables.")
