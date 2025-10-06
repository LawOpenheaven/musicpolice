"""
Main analysis service for Music Police compliance engine
"""
from app.services import rules, settings
from app.services.similarity_detector import (
    calculate_plagiarism_score_with_database,
    store_audio_fingerprint,
    get_analysis_details_with_similarity
)
from app.services.transcription import transcribe_audio
from app.services.lyrics_bias import score_bias, analyze_bias_with_details
from app.services.audio_plagiarism import score_plagiarism, extract_audio_fingerprint
from app.db.models import AnalysisResult, FeedbackRecord
import hashlib
import json
import io
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class FeedbackCreate(BaseModel):
    analysis_result_id: int
    feedback_type: str  # 'correct', 'incorrect', 'partial'
    feedback_details: Optional[str] = None
    user_id: Optional[str] = None


class AnalysisResponse(BaseModel):
    id: int
    filename: str
    compliance_score: float
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    metadata: Dict[str, Any]
    created_at: str


async def run_analysis(file: UploadFile, lyrics: Optional[str], db: Session,
                       priority: str = "normal") -> Dict[str, Any]:
    """
    Run comprehensive compliance analysis on uploaded content
    """
    # Get system settings
    max_file_size = settings.get_setting_value(db, "max_file_size_mb", 100)
    analysis_timeout = settings.get_setting_value(
        db, "analysis_timeout_seconds", 300)

    # Check file size against settings
    file_size_mb = len(await file.read()) / (1024 * 1024)
    await file.seek(0)  # Reset file pointer

    if file_size_mb > max_file_size:
        raise ValueError(
            f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({max_file_size}MB)")

    # Read file content
    raw_content = await file.read()
    file_hash = hashlib.sha256(raw_content).hexdigest()

    # Save audio file for playback
    audio_file_path = save_audio_file(file, raw_content, file_hash)

    # Check if we've already analyzed this exact file
    existing_analysis = db.query(AnalysisResult).filter(
        AnalysisResult.file_hash == file_hash
    ).first()

    if existing_analysis:
        return {
            "id": existing_analysis.id,
            "filename": existing_analysis.filename,
            "compliance_score": existing_analysis.compliance_score,
            "issues": json.loads(existing_analysis.issues_detected),
            "recommendations": json.loads(existing_analysis.recommendations),
            "metadata": json.loads(existing_analysis.analysis_metadata),
            "cached": True
        }

    # Extract audio fingerprint for similarity detection
    audio_fingerprint = extract_audio_fingerprint(
        io.BytesIO(raw_content))

    # Calculate plagiarism score using database comparison
    if audio_fingerprint is not None:
        plagiarism_score, similar_songs = calculate_plagiarism_score_with_database(
            audio_fingerprint, db, threshold=0.7
        )
    else:
        # Fallback to heuristic-based scoring
        plagiarism_score = score_plagiarism(
            io.BytesIO(raw_content), file.filename)
        similar_songs = []

    # Transcribe audio to get lyrics if not provided
    transcribed_lyrics = None
    if not lyrics:
        logger.info(f"Transcribing audio for {file.filename}")
        transcribed_lyrics = transcribe_audio(
            io.BytesIO(raw_content), file.filename)
        if transcribed_lyrics:
            logger.info(
                f"Transcription successful: {len(transcribed_lyrics)} characters")
        else:
            logger.warning(f"Transcription failed for {file.filename}")

    # Use provided lyrics or transcribed lyrics
    final_lyrics = lyrics or transcribed_lyrics

    # Run bias analysis if lyrics available
    bias_score = score_bias(final_lyrics) if final_lyrics else None
    bias_details = analyze_bias_with_details(
        final_lyrics) if final_lyrics else None

    # Get compliance rules from database
    copyright_rule = rules.get_rule_by_type_and_name(
        db, "copyright", "similarity_threshold")
    bias_rule = rules.get_rule_by_type_and_name(
        db, "bias", "toxicity_threshold")
    content_rule = rules.get_rule_by_type_and_name(
        db, "content", "explicit_content_threshold")

    # Calculate compliance score with weighted average
    subscores = []
    weights = []

    if (plagiarism_score is not None and copyright_rule and
            copyright_rule.enabled):
        subscores.append(1.0 - plagiarism_score)
        weights.append(0.5)  # Copyright is weighted higher

    if bias_score is not None and bias_rule and bias_rule.enabled:
        subscores.append(1.0 - bias_score)
        weights.append(0.3)

    if (content_rule and content_rule.enabled and
            bias_score is not None):
        # Use bias score for content filtering
        subscores.append(1.0 - bias_score)
        weights.append(0.2)

    if subscores:
        compliance_score = sum(
            s * w for s, w in zip(subscores, weights)) / sum(weights)
    else:
        compliance_score = 0.0

    # Detect issues based on thresholds
    issues = []

    if (plagiarism_score is not None and copyright_rule and
            copyright_rule.enabled):
        if plagiarism_score > copyright_rule.threshold:
            issues.append({
                "type": "copyright",
                "severity": "high" if plagiarism_score > 0.8 else "medium",
                "confidence": float(plagiarism_score),
                "detail": (f"High similarity detected "
                          f"(score: {plagiarism_score:.2f})")
            })

    if bias_score is not None and bias_rule and bias_rule.enabled:
        if bias_score > bias_rule.threshold:
            issues.append({
                "type": "bias",
                "severity": "high" if bias_score > 0.7 else "medium",
                "confidence": float(bias_score),
                "detail": (f"Potential bias/toxicity detected "
                          f"(score: {bias_score:.2f})")
            })

    # Check content filtering rules
    if content_rule and content_rule.enabled and final_lyrics:
        # Simple explicit content detection based on bias score
        if bias_score is not None and bias_score > content_rule.threshold:
            issues.append({
                "type": "content",
                "severity": "high" if bias_score > 0.8 else "medium",
                "confidence": float(bias_score),
                "detail": (f"Explicit content detected "
                          f"(score: {bias_score:.2f})")
            })

    # Generate recommendations
    recommendations = _generate_recommendations(issues)

    # Store analysis result
    analysis_record = AnalysisResult(
        filename=file.filename,
        file_hash=file_hash,
        compliance_score=float(compliance_score),
        issues_detected=json.dumps(issues),
        recommendations=json.dumps(recommendations),
        analysis_metadata=json.dumps({
            "plagiarism_score": plagiarism_score,
            "bias_score": bias_score,
            "bias_details": bias_details,
            "file_size": len(raw_content),
            "has_lyrics": final_lyrics is not None,
            "lyrics_source": "provided" if lyrics else ("transcribed" if transcribed_lyrics else "none"),
            "transcribed_lyrics": transcribed_lyrics,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }),
        audio_file_path=audio_file_path
    )

    db.add(analysis_record)
    db.commit()
    db.refresh(analysis_record)

    # Store audio fingerprint and similar songs
    if audio_fingerprint is not None:
        store_audio_fingerprint(
            analysis_record.id, audio_fingerprint, similar_songs, db)

    return {
        "id": analysis_record.id,
        "filename": file.filename,
        "compliance_score": compliance_score,
        "issues": issues,
        "recommendations": recommendations,
        "metadata": json.loads(analysis_record.analysis_metadata),
        "similar_songs": similar_songs,
        "cached": False
    }


def _generate_recommendations(issues: List[Dict[str, Any]]) -> List[str]:
    """Generate recommendations based on detected issues"""
    recommendations = []

    for issue in issues:
        if issue["type"] == "copyright":
            recommendations.append(
                "Consider modifying melody, harmony, or rhythm patterns")
            recommendations.append("Increase musical novelty and originality")
            if issue["severity"] == "high":
                recommendations.append(
                    "Significant changes required to avoid copyright infringement")

        elif issue["type"] == "bias":
            recommendations.append(
                "Review lyrics for potentially offensive content")
            recommendations.append(
                "Consider alternative word choices or themes")
            if issue["severity"] == "high":
                recommendations.append(
                    "Content revision strongly recommended before publication")

    if not recommendations:
        recommendations.append("Content appears to meet compliance standards")

    return recommendations


def get_recent_analyses(db: Session, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
    """Get recent analysis results"""
    analyses = db.query(AnalysisResult).order_by(
        desc(AnalysisResult.created_at)
    ).offset(offset).limit(limit).all()

    total_count = db.query(AnalysisResult).count()

    return {
        "analyses": [
            {
                "id": analysis.id,
                "filename": analysis.filename,
                "compliance_score": analysis.compliance_score,
                "issues_count": len(json.loads(analysis.issues_detected)),
                "created_at": analysis.created_at.isoformat()
            }
            for analysis in analyses
        ],
        "total": total_count,
        "limit": limit,
        "offset": offset
    }


def get_analysis_by_id(db: Session, analysis_id: int) -> Dict[str, Any]:
    """Get detailed analysis results by ID"""
    analysis_details = get_analysis_details_with_similarity(analysis_id, db)

    if not analysis_details:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return analysis_details


def submit_feedback(db: Session, feedback: FeedbackCreate) -> Dict[str, str]:
    """Submit feedback on analysis results for adaptive learning"""
    # Verify analysis exists
    analysis = db.query(AnalysisResult).filter(
        AnalysisResult.id == feedback.analysis_result_id
    ).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Store feedback
    feedback_record = FeedbackRecord(
        analysis_result_id=feedback.analysis_result_id,
        feedback_type=feedback.feedback_type,
        feedback_details=feedback.feedback_details,
        user_id=feedback.user_id
    )

    db.add(feedback_record)
    db.commit()

    # TODO: Implement adaptive learning logic here
    # This could update thresholds, retrain models, etc.

    return {"message": "Feedback submitted successfully"}


def get_compliance_stats(db: Session) -> Dict[str, Any]:
    """Get compliance statistics for dashboard"""
    # Get total analyses
    total_analyses = db.query(AnalysisResult).count()

    # Get analyses from last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_analyses = db.query(AnalysisResult).filter(
        AnalysisResult.created_at >= thirty_days_ago
    ).all()

    # Calculate average scores
    if recent_analyses:
        avg_compliance = sum(
            a.compliance_score for a in recent_analyses) / len(recent_analyses)

        # Count issues by type
        copyright_issues = 0
        bias_issues = 0

        for analysis in recent_analyses:
            issues = json.loads(analysis.issues_detected)
            for issue in issues:
                if issue["type"] == "copyright":
                    copyright_issues += 1
                elif issue["type"] == "bias":
                    bias_issues += 1
    else:
        avg_compliance = 0.0
        copyright_issues = 0
        bias_issues = 0

    return {
        "total_analyses": total_analyses,
        "recent_analyses_count": len(recent_analyses),
        "average_compliance_score": round(avg_compliance, 2),
        "copyright_issues_detected": copyright_issues,
        "bias_issues_detected": bias_issues,
        "period": "last_30_days"
    }


def get_dashboard_stats(db: Session) -> Dict[str, Any]:
    """Get dashboard statistics (legacy endpoint)"""
    # Get total analyses
    total_analyses = db.query(AnalysisResult).count()

    # Get analyses from last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_analyses = db.query(AnalysisResult).filter(
        AnalysisResult.created_at >= thirty_days_ago
    ).all()

    # Calculate compliance scores by type
    copyright_scores = []
    bias_scores = []
    content_filter_scores = []

    for analysis in recent_analyses:
        metadata = json.loads(analysis.analysis_metadata)
        if metadata.get("plagiarism_score") is not None:
            copyright_scores.append(1.0 - metadata["plagiarism_score"])
        if metadata.get("bias_score") is not None:
            bias_scores.append(1.0 - metadata["bias_score"])
        # Content filter score is based on overall compliance
        content_filter_scores.append(analysis.compliance_score)

    # Calculate averages - return 0 if no data instead of hardcoded defaults
    avg_copyright = sum(copyright_scores) / \
        len(copyright_scores) * 100 if copyright_scores else 0.0
    avg_bias = sum(bias_scores) / len(bias_scores) * \
        100 if bias_scores else 0.0
    avg_content_filter = sum(content_filter_scores) / \
        len(content_filter_scores) * 100 if content_filter_scores else 0.0

    # Generate trend data for last 7 days
    trend_data = []
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=6-i)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        day_analyses = db.query(AnalysisResult).filter(
            AnalysisResult.created_at >= day_start,
            AnalysisResult.created_at < day_end
        ).count()

        trend_data.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "analyses": day_analyses
        })

    return {
        "total_analyses": total_analyses,
        "compliance_scores": {
            "copyright": round(avg_copyright, 1),
            "bias": round(avg_bias, 1),
            "content_filter": round(avg_content_filter, 1)
        },
        "trend_data": {
            "labels": [item["date"] for item in trend_data],
            "values": [item["analyses"] for item in trend_data]
        },
        "recent_analyses": len(recent_analyses),
        "period": "last_30_days"
    }


def get_reports_summary(
    db: Session,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    analysis_type: Optional[str] = None,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """Get reports summary with filtering"""
    query = db.query(AnalysisResult)

    # Apply date filters
    if start_date:
        start_dt = datetime.fromisoformat(start_date)
        query = query.filter(AnalysisResult.created_at >= start_dt)

    if end_date:
        end_dt = datetime.fromisoformat(end_date)
        query = query.filter(AnalysisResult.created_at <= end_dt)

    analyses = query.all()

    # Filter by analysis type if specified
    if analysis_type and analysis_type != "all":
        filtered_analyses = []
        for analysis in analyses:
            issues = json.loads(analysis.issues_detected)
            if any(issue["type"] == analysis_type for issue in issues):
                filtered_analyses.append(analysis)
        analyses = filtered_analyses

    # Filter by status if specified
    if status and status != "all":
        if status == "completed":
            # Completed analyses have no issues or low-severity issues
            analyses = [
                a for a in analyses
                if len(json.loads(a.issues_detected)) == 0 or
                all(issue.get("severity") != "high"
                    for issue in json.loads(a.issues_detected))
            ]
        elif status == "processing":
            # This would be for ongoing analyses, but we don't have that
            # status in our current model. For now, we'll treat this as
            # analyses with medium-severity issues
            analyses = [
                a for a in analyses
                if any(issue.get("severity") == "medium"
                       for issue in json.loads(a.issues_detected))
            ]
        elif status == "failed":
            # Failed analyses have high-severity issues
            analyses = [
                a for a in analyses
                if any(issue.get("severity") == "high"
                       for issue in json.loads(a.issues_detected))
            ]

    # Calculate summary statistics
    total_analyses = len(analyses)
    if total_analyses > 0:
        avg_compliance = sum(
            a.compliance_score for a in analyses) / total_analyses
        issues_found = sum(len(json.loads(a.issues_detected))
                           for a in analyses)
    else:
        avg_compliance = 0.0
        issues_found = 0

    return {
        "total_analyses": total_analyses,
        "average_compliance_score": round(avg_compliance * 100, 1),
        "issues_found": issues_found,
        "compliance_rate": round((1 - (issues_found / max(total_analyses, 1))) * 100, 1),
        "period": f"{start_date or 'all'} to {end_date or 'now'}"
    }


def get_trend_data(
    db: Session,
    days: int = 30,
    analysis_type: Optional[str] = None
) -> Dict[str, Any]:
    """Get trend data for charts"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Get analyses in the date range
    analyses = db.query(AnalysisResult).filter(
        AnalysisResult.created_at >= start_date,
        AnalysisResult.created_at <= end_date
    ).all()

    # Group by day
    daily_data = {}
    for i in range(days):
        date = start_date + timedelta(days=i)
        date_key = date.strftime("%Y-%m-%d")
        daily_data[date_key] = {
            "analyses": 0,
            "compliance_scores": [],
            "issues": 0
        }

    # Populate daily data
    for analysis in analyses:
        date_key = analysis.created_at.strftime("%Y-%m-%d")
        if date_key in daily_data:
            daily_data[date_key]["analyses"] += 1
            daily_data[date_key]["compliance_scores"].append(
                analysis.compliance_score)

            # Count issues by type if specified
            if analysis_type and analysis_type != "all":
                issues = json.loads(analysis.issues_detected)
                daily_data[date_key]["issues"] += sum(
                    1 for issue in issues if issue["type"] == analysis_type)
            else:
                daily_data[date_key]["issues"] += len(
                    json.loads(analysis.issues_detected))

    # Calculate daily averages
    labels = []
    analysis_counts = []
    avg_scores = []
    issue_counts = []

    for date_key in sorted(daily_data.keys()):
        labels.append(date_key)
        data = daily_data[date_key]
        analysis_counts.append(data["analyses"])

        if data["compliance_scores"]:
            avg_scores.append(
                sum(data["compliance_scores"]) / len(data["compliance_scores"]) * 100)
        else:
            avg_scores.append(0)

        issue_counts.append(data["issues"])

    return {
        "labels": labels,
        "analysis_counts": analysis_counts,
        "average_scores": avg_scores,
        "issue_counts": issue_counts,
        "period": f"last_{days}_days"
    }


def export_report(
    db: Session,
    report_type: str,
    export_format: str = "pdf",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    analysis_type: Optional[str] = None
) -> Dict[str, Any]:
    """Export reports in various formats"""
    # Get the data
    summary = get_reports_summary(db, start_date, end_date, analysis_type)
    trends = get_trend_data(db, 30, analysis_type)

    # For now, return the data structure
    # In a real implementation, you would generate actual PDF/CSV files
    return {
        "report_type": report_type,
        "format": export_format,
        "summary": summary,
        "trends": trends,
        "exported_at": datetime.utcnow().isoformat(),
        "download_url": f"/api/reports/download/{report_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{export_format}"
    }


def save_audio_file(file: UploadFile, raw_content: bytes, file_hash: str) -> str:
    """
    Save uploaded audio file to disk for later playback

    Args:
        file: Uploaded file object
        raw_content: Raw file content
        file_hash: SHA256 hash of the file

    Returns:
        Path to saved audio file
    """
    # Create uploads directory if it doesn't exist
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)

    # Generate filename using hash and original extension
    file_extension = os.path.splitext(
        file.filename)[1] if file.filename else '.mp3'
    audio_filename = f"{file_hash}{file_extension}"
    audio_file_path = os.path.join(uploads_dir, audio_filename)

    # Save file if it doesn't already exist
    if not os.path.exists(audio_file_path):
        with open(audio_file_path, 'wb') as f:
            f.write(raw_content)
        logger.info(f"Saved audio file: {audio_file_path}")
    else:
        logger.info(f"Audio file already exists: {audio_file_path}")

    return audio_file_path
