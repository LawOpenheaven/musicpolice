"""
SQLAlchemy database models for Music Police compliance engine
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class ComplianceRule(Base):
    """
    Model for storing compliance rules and thresholds
    """
    __tablename__ = "compliance_rules"

    id = Column(Integer, primary_key=True, index=True)
    # 'copyright', 'bias', 'content'
    rule_type = Column(String(50), nullable=False)
    rule_name = Column(String(100), nullable=False)
    threshold = Column(Float, default=0.7)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ComplianceRule(id={self.id}, type={self.rule_type}, name={self.rule_name})>"


class AnalysisResult(Base):
    """
    Model for storing analysis results from compliance checks
    """
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=False)
    compliance_score = Column(Float, nullable=False)
    issues_detected = Column(Text)  # JSON string
    recommendations = Column(Text)  # JSON string
    analysis_metadata = Column(Text)  # JSON string
    # JSON string of audio features
    audio_fingerprint = Column(Text, nullable=True)
    # JSON string of similar song IDs
    similar_songs = Column(Text, nullable=True)
    # Path to stored audio file for playback
    audio_file_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, filename={self.filename}, score={self.compliance_score})>"


class FeedbackRecord(Base):
    """
    Model for storing user feedback on analysis results for adaptive learning
    """
    __tablename__ = "feedback_records"

    id = Column(Integer, primary_key=True, index=True)
    # Foreign key to AnalysisResult
    analysis_result_id = Column(Integer, nullable=False)
    # 'correct', 'incorrect', 'partial'
    feedback_type = Column(String(50), nullable=False)
    feedback_details = Column(Text)  # JSON string with detailed feedback
    user_id = Column(String(100))  # Optional user identifier
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<FeedbackRecord(id={self.id}, analysis_id={self.analysis_result_id}, type={self.feedback_type})>"


class SystemSettings(Base):
    """
    Model for storing system-wide configuration settings
    """
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(100), nullable=False, unique=True)
    setting_value = Column(Text, nullable=False)
    # string, int, float, bool
    setting_type = Column(String(20), default="string")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    def __repr__(self):
        return (f"<SystemSettings(key={self.setting_key}, "
                f"value={self.setting_value})>")
