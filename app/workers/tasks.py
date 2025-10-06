"""
Background tasks for Music Police compliance engine
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import AnalysisResult, FeedbackRecord, ComplianceRule
from app.services import analyzer, rules

logger = logging.getLogger(__name__)


class BackgroundTaskManager:
    """Manages background tasks for the application"""

    def __init__(self):
        self.running_tasks = {}

    async def start_analysis_task(self, file_data: bytes, filename: str, lyrics: Optional[str] = None) -> str:
        """Start background analysis task"""
        task_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"

        task = asyncio.create_task(
            self._run_analysis_task(task_id, file_data, filename, lyrics)
        )

        self.running_tasks[task_id] = {
            "task": task,
            "status": "running",
            "started_at": datetime.now(),
            "filename": filename
        }

        return task_id

    async def _run_analysis_task(self, task_id: str, file_data: bytes, filename: str, lyrics: Optional[str] = None):
        """Run analysis task in background"""
        try:
            logger.info(f"Starting background analysis for {filename}")

            # Simulate file upload for analysis
            from fastapi import UploadFile
            from io import BytesIO

            file_obj = UploadFile(
                file=BytesIO(file_data),
                filename=filename
            )

            # Run analysis
            db = SessionLocal()
            try:
                result = await analyzer.run_analysis(file_obj, lyrics, db)

                # Update task status
                self.running_tasks[task_id]["status"] = "completed"
                self.running_tasks[task_id]["result"] = result
                self.running_tasks[task_id]["completed_at"] = datetime.now()

                logger.info(f"Analysis completed for {filename}")

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Analysis failed for {filename}: {e}")
            self.running_tasks[task_id]["status"] = "failed"
            self.running_tasks[task_id]["error"] = str(e)
            self.running_tasks[task_id]["failed_at"] = datetime.now()

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a background task"""
        if task_id not in self.running_tasks:
            return None

        task_info = self.running_tasks[task_id].copy()

        # Remove the actual task object from the response
        if "task" in task_info:
            del task_info["task"]

        return task_info

    def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """Clean up old completed tasks"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        tasks_to_remove = []
        for task_id, task_info in self.running_tasks.items():
            if task_info["status"] in ["completed", "failed"]:
                completed_time = task_info.get(
                    "completed_at") or task_info.get("failed_at")
                if completed_time and completed_time < cutoff_time:
                    tasks_to_remove.append(task_id)

        for task_id in tasks_to_remove:
            del self.running_tasks[task_id]
            logger.info(f"Cleaned up old task: {task_id}")


class AdaptiveLearningWorker:
    """Worker for adaptive learning based on feedback"""

    def __init__(self):
        self.learning_enabled = True

    async def process_feedback_batch(self):
        """Process accumulated feedback to improve models"""
        if not self.learning_enabled:
            return

        db = SessionLocal()
        try:
            # Get recent feedback
            recent_feedback = db.query(FeedbackRecord).filter(
                FeedbackRecord.created_at >= datetime.now() - timedelta(days=7)
            ).all()

            if len(recent_feedback) < 10:  # Need minimum feedback for learning
                logger.info("Not enough feedback for adaptive learning")
                return

            # Analyze feedback patterns
            feedback_analysis = self._analyze_feedback_patterns(
                recent_feedback)

            # Update compliance rules based on feedback
            await self._update_rules_from_feedback(db, feedback_analysis)

            logger.info(
                f"Processed {len(recent_feedback)} feedback records for adaptive learning")

        except Exception as e:
            logger.error(f"Adaptive learning failed: {e}")
        finally:
            db.close()

    def _analyze_feedback_patterns(self, feedback_records) -> Dict[str, Any]:
        """Analyze feedback patterns to identify improvement opportunities"""
        analysis = {
            "total_feedback": len(feedback_records),
            "correct_predictions": 0,
            "incorrect_predictions": 0,
            "partial_predictions": 0,
            "rule_adjustments": {}
        }

        for feedback in feedback_records:
            if feedback.feedback_type == "correct":
                analysis["correct_predictions"] += 1
            elif feedback.feedback_type == "incorrect":
                analysis["incorrect_predictions"] += 1
            elif feedback.feedback_type == "partial":
                analysis["partial_predictions"] += 1

        # Calculate accuracy
        total_predictions = analysis["correct_predictions"] + \
            analysis["incorrect_predictions"]
        if total_predictions > 0:
            accuracy = analysis["correct_predictions"] / total_predictions
            analysis["accuracy"] = accuracy

            # Suggest rule adjustments if accuracy is low
            if accuracy < 0.8:  # Less than 80% accuracy
                # Tighten threshold
                analysis["rule_adjustments"]["similarity_threshold"] = 0.05
                analysis["rule_adjustments"]["toxicity_threshold"] = 0.05

        return analysis

    async def _update_rules_from_feedback(self, db: Session, analysis: Dict[str, Any]):
        """Update compliance rules based on feedback analysis"""
        if "rule_adjustments" not in analysis:
            return

        for rule_name, adjustment in analysis["rule_adjustments"].items():
            # Find the rule
            rule = db.query(ComplianceRule).filter(
                ComplianceRule.rule_name == rule_name
            ).first()

            if rule:
                # Adjust threshold
                new_threshold = max(0.1, min(1.0, rule.threshold + adjustment))
                rule.threshold = new_threshold
                rule.updated_at = datetime.utcnow()

                logger.info(
                    f"Updated {rule_name} threshold to {new_threshold}")

        db.commit()


# Global instances
task_manager = BackgroundTaskManager()
learning_worker = AdaptiveLearningWorker()


async def start_background_workers():
    """Start all background workers"""
    logger.info("Starting background workers...")

    # Start adaptive learning worker (runs every hour)
    asyncio.create_task(periodic_adaptive_learning())

    # Start task cleanup worker (runs every 6 hours)
    asyncio.create_task(periodic_task_cleanup())

    logger.info("Background workers started")


async def periodic_adaptive_learning():
    """Run adaptive learning periodically"""
    while True:
        try:
            await learning_worker.process_feedback_batch()
        except Exception as e:
            logger.error(f"Periodic adaptive learning failed: {e}")

        # Wait 1 hour
        await asyncio.sleep(3600)


async def periodic_task_cleanup():
    """Clean up old tasks periodically"""
    while True:
        try:
            task_manager.cleanup_completed_tasks()
        except Exception as e:
            logger.error(f"Task cleanup failed: {e}")

        # Wait 6 hours
        await asyncio.sleep(21600)
