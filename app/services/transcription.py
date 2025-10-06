"""
Audio transcription service using OpenAI Whisper
"""
import functools
import tempfile
import os
from typing import Optional, BinaryIO
import logging

logger = logging.getLogger(__name__)

# Global variable to store the Whisper model
_whisper_model = None


@functools.lru_cache(maxsize=1)
def _get_whisper_model():
    """
    Get cached Whisper model instance
    Using the 'base' model for good balance of speed and accuracy
    """
    global _whisper_model

    if _whisper_model is None:
        try:
            import whisper

            # Load the base model (good balance of speed and accuracy)
            # Available models: tiny, base, small, medium, large
            # For production, you might want to use 'small' or 'medium'
            _whisper_model = whisper.load_model("base")
            logger.info("Whisper model loaded successfully")

        except ImportError:
            logger.error(
                "Whisper not installed. Install with: pip install openai-whisper")
            return None
        except Exception as e:
            logger.error(f"Error loading Whisper model: {str(e)}")
            return None

    return _whisper_model


def transcribe_audio(file_like: BinaryIO, filename: str = "audio") -> Optional[str]:
    """
    Transcribe audio file to text using Whisper

    Args:
        file_like: Binary file-like object containing audio data
        filename: Name of the file for logging purposes

    Returns:
        Transcribed text or None if transcription fails
    """
    try:
        model = _get_whisper_model()
        if model is None:
            logger.error("Whisper model not available")
            return None

        # Create a temporary file for Whisper processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            # Write audio data to temporary file
            file_like.seek(0)  # Reset file pointer
            temp_file.write(file_like.read())
            temp_file_path = temp_file.name

        try:
            # Transcribe using Whisper
            logger.info(f"Starting transcription for {filename}")
            result = model.transcribe(
                temp_file_path,
                language="en",  # Set to English, remove for auto-detection
                fp16=False,     # Use fp32 for better compatibility
                verbose=False   # Reduce logging
            )

            transcribed_text = result["text"].strip()

            if transcribed_text:
                logger.info(
                    f"Transcription completed for {filename}: {len(transcribed_text)} characters")
                return transcribed_text
            else:
                logger.warning(f"No text transcribed from {filename}")
                return None

        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass

    except Exception as e:
        logger.error(f"Error transcribing audio for {filename}: {str(e)}")
        return None


def transcribe_audio_with_timestamps(file_like: BinaryIO, filename: str = "audio") -> Optional[dict]:
    """
    Transcribe audio with word-level timestamps

    Args:
        file_like: Binary file-like object containing audio data
        filename: Name of the file for logging purposes

    Returns:
        Dictionary with transcription and timing information
    """
    try:
        model = _get_whisper_model()
        if model is None:
            return None

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            file_like.seek(0)
            temp_file.write(file_like.read())
            temp_file_path = temp_file.name

        try:
            # Transcribe with word timestamps
            result = model.transcribe(
                temp_file_path,
                language="en",
                fp16=False,
                word_timestamps=True,
                verbose=False
            )

            # Extract segments with timestamps
            segments = []
            for segment in result.get("segments", []):
                segments.append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"].strip()
                })

            return {
                "text": result["text"].strip(),
                "segments": segments,
                "language": result.get("language", "en")
            }

        finally:
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass

    except Exception as e:
        logger.error(
            f"Error transcribing audio with timestamps for {filename}: {str(e)}")
        return None


def get_available_models():
    """
    Get list of available Whisper models
    """
    try:
        import whisper
        return whisper.available_models()
    except ImportError:
        return []


def is_whisper_available() -> bool:
    """
    Check if Whisper is available and working
    """
    try:
        model = _get_whisper_model()
        return model is not None
    except Exception:
        return False
