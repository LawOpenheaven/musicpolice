"""
Audio similarity detection service for plagiarism detection
"""
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
# from scipy.spatial.distance import cosine  # Unused import
import logging

from app.db.models import AnalysisResult
from app.services.audio_plagiarism import compare_fingerprints

logger = logging.getLogger(__name__)


def find_similar_songs(
    new_fingerprint: np.ndarray,
    db: Session,
    threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Find songs similar to the new upload based on audio fingerprint comparison

    Args:
        new_fingerprint: Audio fingerprint of the new upload
        db: Database session
        threshold: Similarity threshold (0.0 to 1.0)

    Returns:
        List of similar songs with similarity scores
    """
    try:
        # Get all existing analysis results with fingerprints
        existing_analyses = db.query(AnalysisResult).filter(
            AnalysisResult.audio_fingerprint.isnot(None)
        ).all()

        similar_songs = []

        for analysis in existing_analyses:
            try:
                # Parse stored fingerprint
                stored_fingerprint_data = json.loads(
                    analysis.audio_fingerprint)
                stored_fingerprint = np.array(stored_fingerprint_data)

                # Calculate similarity
                similarity = compare_fingerprints(
                    new_fingerprint, stored_fingerprint)

                # If similarity exceeds threshold, add to results
                if similarity >= threshold:
                    similar_songs.append({
                        "id": analysis.id,
                        "filename": analysis.filename,
                        "similarity_score": float(similarity),
                        "compliance_score": analysis.compliance_score,
                        "created_at": analysis.created_at.isoformat(),
                        "file_hash": analysis.file_hash
                    })

            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logger.warning(
                    f"Error processing fingerprint for analysis {analysis.id}: {e}")
                continue

        # Sort by similarity score (highest first)
        similar_songs.sort(key=lambda x: x["similarity_score"], reverse=True)

        logger.info(
            f"Found {len(similar_songs)} similar songs above threshold {threshold}")
        return similar_songs

    except Exception as e:
        logger.error(f"Error finding similar songs: {e}")
        return []


def calculate_plagiarism_score_with_database(
    new_fingerprint: np.ndarray,
    db: Session,
    threshold: float = 0.7
) -> Tuple[float, List[Dict[str, Any]]]:
    """
    Calculate plagiarism score based on database comparison

    Args:
        new_fingerprint: Audio fingerprint of the new upload
        db: Database session
        threshold: Similarity threshold for plagiarism detection

    Returns:
        Tuple of (plagiarism_score, similar_songs_list)
    """
    try:
        # Find similar songs
        similar_songs = find_similar_songs(new_fingerprint, db, threshold)

        if not similar_songs:
            # No similar songs found
            return 0.0, []

        # Calculate plagiarism score based on highest similarity
        highest_similarity = similar_songs[0]["similarity_score"]

        # Scale the similarity to plagiarism score
        # If similarity is above threshold, it's considered plagiarism
        if highest_similarity >= threshold:
            # Scale from threshold to 1.0 for plagiarism score
            plagiarism_score = (highest_similarity -
                                threshold) / (1.0 - threshold)
            plagiarism_score = min(1.0, plagiarism_score)  # Cap at 1.0
        else:
            plagiarism_score = 0.0

        logger.info(
            f"Plagiarism score: {plagiarism_score:.3f} (highest similarity: {highest_similarity:.3f})")

        return plagiarism_score, similar_songs

    except Exception as e:
        logger.error(f"Error calculating plagiarism score: {e}")
        return 0.0, []


def store_audio_fingerprint(
    analysis_id: int,
    fingerprint: np.ndarray,
    similar_songs: List[Dict[str, Any]],
    db: Session
) -> bool:
    """
    Store audio fingerprint and similar songs in database

    Args:
        analysis_id: ID of the analysis result
        fingerprint: Audio fingerprint to store
        similar_songs: List of similar songs
        db: Database session

    Returns:
        True if successful, False otherwise
    """
    try:
        # Get the analysis result
        analysis = db.query(AnalysisResult).filter(
            AnalysisResult.id == analysis_id
        ).first()

        if not analysis:
            logger.error(f"Analysis result {analysis_id} not found")
            return False

        # Convert fingerprint to JSON-serializable format
        fingerprint_data = fingerprint.tolist()

        # Store fingerprint and similar songs
        analysis.audio_fingerprint = json.dumps(fingerprint_data)
        analysis.similar_songs = json.dumps(similar_songs)

        db.commit()

        logger.info(
            f"Stored fingerprint and {len(similar_songs)} similar songs for analysis {analysis_id}")
        return True

    except Exception as e:
        logger.error(f"Error storing audio fingerprint: {e}")
        db.rollback()
        return False


def get_similar_songs_for_analysis(analysis_id: int, db: Session) -> List[Dict[str, Any]]:
    """
    Get similar songs for a specific analysis

    Args:
        analysis_id: ID of the analysis result
        db: Database session

    Returns:
        List of similar songs
    """
    try:
        analysis = db.query(AnalysisResult).filter(
            AnalysisResult.id == analysis_id
        ).first()

        if not analysis or not analysis.similar_songs:
            return []

        similar_songs = json.loads(analysis.similar_songs)
        return similar_songs

    except Exception as e:
        logger.error(
            f"Error getting similar songs for analysis {analysis_id}: {e}")
        return []


def get_analysis_lyrics(analysis_id: int, db: Session) -> Optional[str]:
    """
    Get transcribed lyrics for a specific analysis

    Args:
        analysis_id: ID of the analysis result
        db: Database session

    Returns:
        Transcribed lyrics or None if not available
    """
    try:
        analysis = db.query(AnalysisResult).filter(
            AnalysisResult.id == analysis_id
        ).first()

        if not analysis or not analysis.analysis_metadata:
            return None

        metadata = json.loads(analysis.analysis_metadata)
        return metadata.get("transcribed_lyrics")

    except Exception as e:
        logger.error(f"Error getting lyrics for analysis {analysis_id}: {e}")
        return None


def get_analysis_details_with_similarity(analysis_id: int, db: Session) -> Optional[Dict[str, Any]]:
    """
    Get complete analysis details including similar songs and lyrics

    Args:
        analysis_id: ID of the analysis result
        db: Database session

    Returns:
        Complete analysis details or None if not found
    """
    try:
        analysis = db.query(AnalysisResult).filter(
            AnalysisResult.id == analysis_id
        ).first()

        if not analysis:
            return None

        # Parse metadata
        metadata = json.loads(
            analysis.analysis_metadata) if analysis.analysis_metadata else {}

        # Get similar songs
        similar_songs = get_similar_songs_for_analysis(analysis_id, db)

        # Get lyrics
        lyrics = metadata.get("transcribed_lyrics")

        return {
            "id": analysis.id,
            "filename": analysis.filename,
            "compliance_score": analysis.compliance_score,
            "issues": json.loads(analysis.issues_detected) if analysis.issues_detected else [],
            "recommendations": json.loads(analysis.recommendations) if analysis.recommendations else [],
            "metadata": metadata,
            "similar_songs": similar_songs,
            "lyrics": lyrics,
            "created_at": analysis.created_at.isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting analysis details: {e}")
        return None


def get_similarity_analysis_details(analysis_id: int, db: Session) -> Optional[Dict[str, Any]]:
    """
    Get detailed similarity analysis with visual representation data

    Args:
        analysis_id: ID of the analysis result
        db: Database session

    Returns:
        Detailed similarity analysis or None if not found
    """
    try:
        analysis = db.query(AnalysisResult).filter(
            AnalysisResult.id == analysis_id
        ).first()

        if not analysis:
            return None

        # Parse metadata
        metadata = json.loads(
            analysis.analysis_metadata) if analysis.analysis_metadata else {}

        # Get similar songs with enhanced details
        similar_songs = get_similar_songs_for_analysis(analysis_id, db)

        # Enhance similar songs with additional metadata
        enhanced_similar_songs = []
        for song in similar_songs:
            # Get the original analysis for this similar song
            original_analysis = db.query(AnalysisResult).filter(
                AnalysisResult.id == song["id"]
            ).first()

            if original_analysis:
                original_metadata = json.loads(
                    original_analysis.analysis_metadata) if original_analysis.analysis_metadata else {}

                enhanced_song = {
                    **song,
                    "original_filename": original_analysis.filename,
                    "original_compliance_score": original_analysis.compliance_score,
                    "original_created_at": original_analysis.created_at.isoformat(),
                    "audio_features": {
                        "plagiarism_score": original_metadata.get("plagiarism_score", 0.0),
                        "bias_score": original_metadata.get("bias_score", 0.0),
                        "has_lyrics": original_metadata.get("has_lyrics", False)
                    },
                    "similarity_breakdown": _generate_similarity_breakdown(song["similarity_score"])
                }
                enhanced_similar_songs.append(enhanced_song)

        # Get current analysis fingerprint for comparison
        current_fingerprint = None
        if analysis.audio_fingerprint:
            current_fingerprint = json.loads(analysis.audio_fingerprint)

        return {
            "analysis_id": analysis_id,
            "current_song": {
                "filename": analysis.filename,
                "compliance_score": analysis.compliance_score,
                "created_at": analysis.created_at.isoformat(),
                "audio_fingerprint": current_fingerprint
            },
            "similar_songs": enhanced_similar_songs,
            "similarity_summary": {
                "total_similar_songs": len(enhanced_similar_songs),
                "highest_similarity": max([s["similarity_score"] for s in enhanced_similar_songs], default=0.0),
                "average_similarity": sum([s["similarity_score"] for s in enhanced_similar_songs]) / len(enhanced_similar_songs) if enhanced_similar_songs else 0.0,
                "similarity_threshold": 0.7
            }
        }

    except Exception as e:
        logger.error(f"Error getting similarity analysis details: {e}")
        return None


def _generate_similarity_breakdown(similarity_score: float) -> Dict[str, Any]:
    """
    Generate a breakdown of similarity score for visual representation
    """
    if similarity_score >= 0.9:
        level = "very_high"
        description = "Very high similarity - potential direct copy"
        color = "#ff4444"
    elif similarity_score >= 0.8:
        level = "high"
        description = "High similarity - significant resemblance"
        color = "#ff8800"
    elif similarity_score >= 0.7:
        level = "medium"
        description = "Medium similarity - some resemblance"
        color = "#ffaa00"
    elif similarity_score >= 0.5:
        level = "low"
        description = "Low similarity - minor resemblance"
        color = "#88cc00"
    else:
        level = "very_low"
        description = "Very low similarity - minimal resemblance"
        color = "#44aa44"

    return {
        "level": level,
        "description": description,
        "color": color,
        "percentage": int(similarity_score * 100)
    }
