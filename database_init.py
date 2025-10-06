"""
Database initialization script for Music Police
Run this script to set up the database with tables and default data
"""
from app.db.database import init_database, test_database_connection
import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


if __name__ == "__main__":
    print("🎼 Music Police - Database Initialization")
    print("=" * 50)

    # Test connection first
    if test_database_connection():
        print("✅ Database connection successful")

        # Initialize database
        init_database()
        print("✅ Database initialization complete")

        print("\n🚀 Database is ready! You can now run the application.")
        print("Run: python -m app.main")

    else:
        print("❌ Database connection failed")
        print("\n📋 Please check:")
        print("1. PostgreSQL is running")
        print("2. Database 'musicpolice_db' exists")
        print("3. User 'musicpolice_user' has proper permissions")
        print("4. Connection string in config is correct")
