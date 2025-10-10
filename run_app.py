#!/usr/bin/env python3
"""
🎼 Music Police - Application Runner
Simple script to run the Music Police application with proper database integration
"""
import sys
import os
import subprocess
from pathlib import Path

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


def main():
    print("🎼 Music Police - Application Runner")
    print("=" * 50)

    try:
        # Check if database is set up
        print("📡 Checking database connection...")
        from app.db.database import test_database_connection

        if not test_database_connection():
            print("❌ Database connection failed")
            print("\n🔧 Setting up database...")

            # Run database initialization
            result = subprocess.run([sys.executable, "database_init.py"],
                                    capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Database setup failed: {result.stderr}")
                return
            print("✅ Database setup complete")

        print("✅ Database connection successful")
        print("\n🚀 Starting Music Police application...")
        print("📱 Dashboard: http://127.0.0.1:8000")
        print("📚 API Docs: http://127.0.0.1:8000/docs")
        print("🔍 API Monitor: http://127.0.0.1:8000/api-monitor")
        print("\nPress Ctrl+C to stop the server")
        print("-" * 50)

        # Run the proper application
        subprocess.run([sys.executable, "-m", "app.main"])

    except KeyboardInterrupt:
        print("\n👋 Music Police stopped")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(
            "Make sure you're in the correct directory and all dependencies are installed")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
