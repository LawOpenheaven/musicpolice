"""
Compliance rules management service
"""
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.models import ComplianceRule
from fastapi import HTTPException


class RuleCreate(BaseModel):
    rule_type: str
    rule_name: str
    threshold: float = 0.7
    enabled: bool = True


class RuleUpdate(BaseModel):
    rule_name: Optional[str] = None
    threshold: Optional[float] = None
    enabled: Optional[bool] = None


class RuleResponse(BaseModel):
    id: int
    rule_type: str
    rule_name: str
    threshold: float
    enabled: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


def list_rules(db: Session) -> List[ComplianceRule]:
    """Get all compliance rules"""
    return db.query(ComplianceRule).all()


def create_rule(db: Session, rule_data: RuleCreate) -> ComplianceRule:
    """Create a new compliance rule"""
    rule = ComplianceRule(**rule_data.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def update_rule(db: Session, rule_id: int, rule_update: RuleUpdate) -> ComplianceRule:
    """Update an existing compliance rule"""
    rule = db.query(ComplianceRule).filter(
        ComplianceRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    update_data = rule_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)

    db.commit()
    db.refresh(rule)
    return rule


def delete_rule(db: Session, rule_id: int) -> dict:
    """Delete a compliance rule"""
    rule = db.query(ComplianceRule).filter(
        ComplianceRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    db.delete(rule)
    db.commit()
    return {"message": "Rule deleted successfully"}


def get_rule_by_type_and_name(db: Session, rule_type: str, rule_name: str) -> Optional[ComplianceRule]:
    """Get a specific rule by type and name"""
    return db.query(ComplianceRule).filter(
        ComplianceRule.rule_type == rule_type,
        ComplianceRule.rule_name == rule_name,
        ComplianceRule.enabled == True
    ).first()
