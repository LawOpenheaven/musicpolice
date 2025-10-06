"""
Database initialization and utility functions
"""
from app.db.session import create_tables, get_db, SessionLocal
from app.db.models import ComplianceRule, AnalysisResult, FeedbackRecord, SystemSettings
from sqlalchemy.orm import Session


def init_database():
    """
    Initialize database with tables and default data
    """
    # Create tables first
    create_tables()
    print("✅ Tables created successfully!")

    # Add default compliance rules
    db = SessionLocal()
    try:
        # Check if rules already exist
        existing_rules = db.query(ComplianceRule).count()
        if existing_rules == 0:
            default_rules = [
                ComplianceRule(
                    rule_type="copyright",
                    rule_name="similarity_threshold",
                    threshold=0.7,
                    enabled=True
                ),
                ComplianceRule(
                    rule_type="bias",
                    rule_name="toxicity_threshold",
                    threshold=0.4,
                    enabled=True
                ),
                ComplianceRule(
                    rule_type="content",
                    rule_name="explicit_content_threshold",
                    threshold=0.6,
                    enabled=True
                )
            ]

            for rule in default_rules:
                db.add(rule)

            db.commit()
            print("✅ Default compliance rules created")
        else:
            print("✅ Compliance rules already exist")

        # Initialize default system settings
        from app.services import settings
        settings.initialize_default_settings(db)
        print("✅ Default system settings created")

        print("✅ Database initialization complete")

    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()


def test_database_connection():
    """
    Test database connection and basic operations
    """
    try:
        from sqlalchemy import text
        db = SessionLocal()

        # Test basic connection with a simple query
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        print(f"✅ Database connection successful.")

        db.close()
        return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
