"""
API routes for Music Police compliance engine
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.services import analyzer, rules, settings

router = APIRouter()


@router.get("/health")
def health_check():
    """Health check endpoint for the API"""
    from app.services.transcription import is_whisper_available

    return {
        "status": "healthy",
        "service": "Music Police API",
        "whisper_available": is_whisper_available(),
        "features": {
            "audio_analysis": True,
            "transcription": is_whisper_available(),
            "bias_detection": True,
            "background_tasks": True
        }
    }


@router.get("/rules")
def list_compliance_rules(db: Session = Depends(get_db)):
    """Get all compliance rules structured for frontend"""
    all_rules = rules.list_rules(db)

    # Structure rules for frontend
    structured_rules = {
        "copyright_rules": {
            "enabled": False,
            "similarity_threshold": 0.7
        },
        "bias_detection": {
            "enabled": False,
            "toxicity_threshold": 0.4,
            "categories": ["gender", "race", "age"]
        },
        "content_filtering": {
            "explicit_content": False,
            "explicit_content_threshold": 0.6,
            "hate_speech": True
        }
    }

    # Map database rules to structured format
    for rule in all_rules:
        if (rule.rule_type == "copyright" and
                rule.rule_name == "similarity_threshold"):
            structured_rules["copyright_rules"]["enabled"] = rule.enabled
            structured_rules["copyright_rules"]["similarity_threshold"] = (
                rule.threshold)
        elif (rule.rule_type == "bias" and
              rule.rule_name == "toxicity_threshold"):
            structured_rules["bias_detection"]["enabled"] = rule.enabled
            structured_rules["bias_detection"]["toxicity_threshold"] = (
                rule.threshold)
        elif (rule.rule_type == "content" and
              rule.rule_name == "explicit_content_threshold"):
            structured_rules["content_filtering"]["explicit_content"] = (
                rule.enabled)
            structured_rules["content_filtering"]["explicit_content_threshold"] = (
                rule.threshold)

    return structured_rules


@router.post("/rules")
def save_compliance_rules(rules_data: dict, db: Session = Depends(get_db)):
    """Save compliance rules from frontend"""
    try:
        # Update copyright rules
        if "copyright_rules" in rules_data:
            copyright_rule = rules.get_rule_by_type_and_name(
                db, "copyright", "similarity_threshold")
            if copyright_rule:
                rules.update_rule(db, copyright_rule.id, rules.RuleUpdate(
                    enabled=rules_data["copyright_rules"].get("enabled", True),
                    threshold=rules_data["copyright_rules"].get(
                        "similarity_threshold", 0.7)
                ))
            else:
                rules.create_rule(db, rules.RuleCreate(
                    rule_type="copyright",
                    rule_name="similarity_threshold",
                    threshold=rules_data["copyright_rules"].get(
                        "similarity_threshold", 0.7),
                    enabled=rules_data["copyright_rules"].get("enabled", True)
                ))

        # Update bias detection rules
        if "bias_detection" in rules_data:
            bias_rule = rules.get_rule_by_type_and_name(
                db, "bias", "toxicity_threshold")
            if bias_rule:
                rules.update_rule(db, bias_rule.id, rules.RuleUpdate(
                    enabled=rules_data["bias_detection"].get("enabled", True),
                    threshold=rules_data["bias_detection"].get(
                        "toxicity_threshold", 0.4)
                ))
            else:
                rules.create_rule(db, rules.RuleCreate(
                    rule_type="bias",
                    rule_name="toxicity_threshold",
                    threshold=rules_data["bias_detection"].get(
                        "toxicity_threshold", 0.4),
                    enabled=rules_data["bias_detection"].get("enabled", True)
                ))

        # Update content filtering rules
        if "content_filtering" in rules_data:
            content_rule = rules.get_rule_by_type_and_name(
                db, "content", "explicit_content_threshold")
            if content_rule:
                rules.update_rule(db, content_rule.id, rules.RuleUpdate(
                    enabled=rules_data["content_filtering"].get(
                        "explicit_content", True),
                    threshold=rules_data["content_filtering"].get(
                        "explicit_content_threshold", 0.6)
                ))
            else:
                rules.create_rule(db, rules.RuleCreate(
                    rule_type="content",
                    rule_name="explicit_content_threshold",
                    threshold=rules_data["content_filtering"].get(
                        "explicit_content_threshold", 0.6),
                    enabled=rules_data["content_filtering"].get(
                        "explicit_content", True)
                ))

        return {"message": "Rules saved successfully", "status": "success"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error saving rules: {str(e)}")


@router.get("/settings")
def get_system_settings(db: Session = Depends(get_db)):
    """Get all system settings"""
    return settings.get_all_settings(db)


@router.post("/settings")
def save_system_settings(settings_data: dict, db: Session = Depends(get_db)):
    """Save system settings"""
    try:
        # Map frontend settings to database keys
        setting_mappings = {
            "default-priority": ("default_priority", "string"),
            "auto-delete": ("auto_delete_days", "int"),
            "email-notifications": ("email_notifications", "bool"),
            "rate-limit": ("api_rate_limit", "int"),
            "max-file-size": ("max_file_size_mb", "int"),
            "api-logging": ("api_logging", "bool"),
            "require-auth": ("require_auth", "bool"),
            "encrypt-files": ("encrypt_files", "bool"),
            "session-timeout": ("session_timeout_minutes", "int")
        }

        for frontend_key, (db_key, setting_type) in setting_mappings.items():
            if frontend_key in settings_data:
                value = settings_data[frontend_key]
                settings.set_setting(db, db_key, value, setting_type)

        return {"message": "Settings saved successfully", "status": "success"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error saving settings: {str(e)}")


@router.get("/settings/{key}")
def get_setting(key: str, db: Session = Depends(get_db)):
    """Get a specific setting"""
    setting = settings.get_setting(db, key)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return settings.SettingResponse.from_orm(setting)


@router.put("/rules/{rule_id}")
def update_compliance_rule(
    rule_id: int,
    rule_update: rules.RuleUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing compliance rule"""
    return rules.update_rule(db, rule_id, rule_update)


@router.delete("/rules/{rule_id}")
def delete_compliance_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete a compliance rule"""
    return rules.delete_rule(db, rule_id)


@router.post("/analyze")
async def analyze_content(
    file: UploadFile = File(...),
    lyrics: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Analyze uploaded audio file for compliance
    """
    # Validate file type
    if not any(file.filename.lower().endswith(ext) for ext in ['.mp3', '.wav', '.flac', '.m4a', '.ogg']):
        raise HTTPException(status_code=400, detail="Unsupported file format")

    # Get priority from form data or use default
    priority = form_data.get("priority", "normal")

    # Run analysis
    result = await analyzer.run_analysis(file, lyrics, db, priority)
    return result


@router.get("/analyses")
def get_recent_analyses(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get recent analysis results"""
    return analyzer.get_recent_analyses(db, limit, offset)


@router.get("/analyses/{analysis_id}")
def get_analysis_details(analysis_id: int, db: Session = Depends(get_db)):
    """Get detailed analysis results by ID"""
    return analyzer.get_analysis_by_id(db, analysis_id)


@router.get("/analyses/{analysis_id}/lyrics")
def get_analysis_lyrics(analysis_id: int, db: Session = Depends(get_db)):
    """Get transcribed lyrics for a specific analysis"""
    from app.services.similarity_detector import get_analysis_lyrics

    lyrics = get_analysis_lyrics(analysis_id, db)
    if lyrics is None:
        raise HTTPException(
            status_code=404, detail="Lyrics not found for this analysis")

    return {
        "analysis_id": analysis_id,
        "lyrics": lyrics,
        "source": "transcribed"  # Could be "provided" or "transcribed"
    }


@router.get("/analyses/{analysis_id}/similar")
def get_similar_songs(analysis_id: int, db: Session = Depends(get_db)):
    """Get similar songs for a specific analysis"""
    from app.services.similarity_detector import get_similar_songs_for_analysis

    similar_songs = get_similar_songs_for_analysis(analysis_id, db)

    return {
        "analysis_id": analysis_id,
        "similar_songs": similar_songs,
        "count": len(similar_songs)
    }


@router.get("/analyses/{analysis_id}/bias-details")
def get_bias_analysis_details(analysis_id: int, db: Session = Depends(get_db)):
    """Get detailed bias analysis with word-level information"""
    from app.db.models import AnalysisResult
    import json

    # Get analysis from database
    analysis = db.query(AnalysisResult).filter(
        AnalysisResult.id == analysis_id).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Get bias details from metadata
    metadata = json.loads(
        analysis.analysis_metadata) if analysis.analysis_metadata else {}
    bias_details = metadata.get("bias_details")

    if not bias_details:
        raise HTTPException(
            status_code=404, detail="Bias analysis not available")

    return {
        "analysis_id": analysis_id,
        "filename": analysis.filename,
        "bias_analysis": bias_details
    }


@router.get("/analyses/{analysis_id}/similarity-details")
def get_similarity_analysis_details(analysis_id: int, db: Session = Depends(get_db)):
    """Get detailed similarity analysis with visual representation data"""
    from app.services.similarity_detector import get_similarity_analysis_details

    similarity_details = get_similarity_analysis_details(analysis_id, db)

    if not similarity_details:
        raise HTTPException(
            status_code=404, detail="Similarity analysis not found")

    return similarity_details


@router.post("/feedback")
def submit_feedback(
    feedback: analyzer.FeedbackCreate,
    db: Session = Depends(get_db)
):
    """Submit feedback on analysis results for adaptive learning"""
    return analyzer.submit_feedback(db, feedback)


@router.get("/stats")
def get_compliance_stats(db: Session = Depends(get_db)):
    """Get compliance statistics for dashboard"""
    return analyzer.get_compliance_stats(db)


# Background task endpoints
@router.post("/analyze/async")
async def analyze_content_async(
    file: UploadFile = File(...),
    lyrics: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Start background analysis of uploaded audio file
    """
    # Validate file type
    if not any(file.filename.lower().endswith(ext) for ext in ['.mp3', '.wav', '.flac', '.m4a', '.ogg']):
        raise HTTPException(status_code=400, detail="Unsupported file format")

    # Read file content
    file_content = await file.read()

    # Start background task
    from app.workers.tasks import task_manager
    task_id = await task_manager.start_analysis_task(file_content, file.filename, lyrics)

    return {
        "task_id": task_id,
        "status": "started",
        "message": "Analysis started in background"
    }


@router.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    """Get status of a background analysis task"""
    from app.workers.tasks import task_manager
    status = task_manager.get_task_status(task_id)

    if status is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return status


@router.get("/analyses/{analysis_id}/audio")
def get_analysis_audio(analysis_id: int, db: Session = Depends(get_db)):
    """Get audio file for a specific analysis"""
    from app.db.models import AnalysisResult
    from fastapi.responses import FileResponse
    import os

    # Get analysis from database
    analysis = db.query(AnalysisResult).filter(
        AnalysisResult.id == analysis_id).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Check if audio file exists
    if not analysis.audio_file_path or not os.path.exists(analysis.audio_file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")

    # Return the audio file
    return FileResponse(
        path=analysis.audio_file_path,
        media_type="audio/mpeg",
        filename=analysis.filename
    )


@router.put("/analyses/{analysis_id}/lyrics")
def update_analysis_lyrics(analysis_id: int, lyrics_data: dict, db: Session = Depends(get_db)):
    """Update lyrics for a specific analysis"""
    from app.db.models import AnalysisResult
    import json

    # Get analysis from database
    analysis = db.query(AnalysisResult).filter(
        AnalysisResult.id == analysis_id).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Update lyrics in metadata
    metadata = json.loads(analysis.analysis_metadata)
    metadata["transcribed_lyrics"] = lyrics_data.get("lyrics", "")
    metadata["lyrics_source"] = "edited"

    # Update the analysis record
    analysis.analysis_metadata = json.dumps(metadata)
    db.commit()
    db.refresh(analysis)

    return {"message": "Lyrics updated successfully", "analysis_id": analysis_id}


@router.get("/tasks")
def list_background_tasks():
    """List all background tasks"""
    from app.workers.tasks import task_manager

    tasks = []
    for task_id, task_info in task_manager.running_tasks.items():
        task_data = task_info.copy()
        if "task" in task_data:
            del task_data["task"]
        task_data["task_id"] = task_id
        tasks.append(task_data)

    return {
        "tasks": tasks,
        "total": len(tasks)
    }


# Legacy endpoints for backward compatibility
@router.get("/dashboard-stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics (legacy endpoint)"""
    return analyzer.get_dashboard_stats(db)


@router.get("/recent-analyses")
def get_recent_analyses_legacy(db: Session = Depends(get_db)):
    """Get recent analyses (legacy endpoint)"""
    return analyzer.get_recent_analyses(db, limit=10, offset=0)


# Reports endpoints
@router.get("/reports/summary")
def get_reports_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    analysis_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get reports summary with filtering"""
    return analyzer.get_reports_summary(db, start_date, end_date, analysis_type, status)


@router.get("/reports/trends")
def get_trend_data(
    days: int = 30,
    analysis_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get trend data for charts"""
    return analyzer.get_trend_data(db, days, analysis_type)


@router.post("/reports/export")
def export_report(
    request_data: dict,
    db: Session = Depends(get_db)
):
    """Export reports in various formats"""
    report_type = request_data.get("report_type", "compliance_summary")
    export_format = request_data.get("format", "pdf")
    start_date = request_data.get("start_date")
    end_date = request_data.get("end_date")
    analysis_type = request_data.get("analysis_type")

    return analyzer.export_report(db, report_type, export_format, start_date, end_date, analysis_type)
