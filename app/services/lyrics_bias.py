"""
Lyrics bias and toxicity detection service using transformer models
"""
import functools
from typing import Optional
from transformers import pipeline
import logging

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1)
def _get_toxicity_classifier():
    """
    Get cached toxicity classification pipeline
    Using a lightweight model for bias/toxicity detection
    """
    try:
        # Using a more accessible model for toxicity detection
        # You can replace this with other models like:
        # - "unitary/toxic-bert" (if available)
        # - "martin-ha/toxic-comment-model"
        # - "s-nlp/roberta_toxicity_classifier"

        classifier = pipeline(
            "text-classification",
            model="cardiffnlp/twitter-roberta-base-offensive",
            truncation=True,
            max_length=512
        )
        logger.info("Toxicity classifier loaded successfully")
        return classifier

    except Exception as e:
        logger.error(f"Error loading toxicity classifier: {str(e)}")
        # Fallback to a simpler approach if model loading fails
        return None


@functools.lru_cache(maxsize=1)
def _get_sentiment_classifier():
    """
    Get cached sentiment analysis pipeline as backup
    """
    try:
        classifier = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            truncation=True,
            max_length=512
        )
        logger.info("Sentiment classifier loaded successfully")
        return classifier

    except Exception as e:
        logger.error(f"Error loading sentiment classifier: {str(e)}")
        return None


def score_bias(text: Optional[str]) -> Optional[float]:
    """
    Analyze text for potential bias, toxicity, or offensive content

    Args:
        text: Input text (lyrics) to analyze

    Returns:
        Float between 0.0 and 1.0 indicating bias/toxicity likelihood
        (0.0 = no bias detected, 1.0 = high bias/toxicity)
        None if text is empty or analysis fails
    """
    if not text or not text.strip():
        return None

    try:
        # Clean and prepare text
        cleaned_text = _preprocess_text(text)

        if not cleaned_text:
            return 0.0

        # Try toxicity classifier first
        toxicity_classifier = _get_toxicity_classifier()

        if toxicity_classifier:
            return _analyze_with_toxicity_model(cleaned_text, toxicity_classifier)

        # Fallback to sentiment analysis
        sentiment_classifier = _get_sentiment_classifier()

        if sentiment_classifier:
            return _analyze_with_sentiment_model(cleaned_text, sentiment_classifier)

        # Final fallback to keyword-based analysis
        return _analyze_with_keywords(cleaned_text)

    except Exception as e:
        logger.error(f"Error in bias analysis: {str(e)}")
        return 0.0


def _preprocess_text(text: str) -> str:
    """
    Clean and preprocess text for analysis
    """
    # Remove excessive whitespace
    cleaned = " ".join(text.split())

    # Limit length to avoid model limitations
    if len(cleaned) > 2000:
        cleaned = cleaned[:2000] + "..."

    return cleaned


def _analyze_with_toxicity_model(text: str, classifier) -> float:
    """
    Analyze text using toxicity classification model
    """
    try:
        results = classifier(text)

        # Handle different model output formats
        if isinstance(results, list):
            results = results[0]

        # Look for offensive/toxic labels
        label = results.get('label', '').lower()
        score = results.get('score', 0.0)

        # Different models use different labels
        if any(keyword in label for keyword in ['offensive', 'toxic', 'hate', 'negative']):
            return float(score)
        else:
            return float(1.0 - score)  # Invert if label indicates non-toxic

    except Exception as e:
        logger.error(f"Error in toxicity model analysis: {str(e)}")
        return 0.0


def _analyze_with_sentiment_model(text: str, classifier) -> float:
    """
    Analyze text using sentiment analysis as a proxy for bias detection
    """
    try:
        results = classifier(text)

        if isinstance(results, list):
            results = results[0]

        label = results.get('label', '').lower()
        score = results.get('score', 0.0)

        # Convert sentiment to bias score
        if 'negative' in label:
            # High negative sentiment might indicate problematic content
            return float(score * 0.7)  # Scale down since sentiment != toxicity
        else:
            return 0.0

    except Exception as e:
        logger.error(f"Error in sentiment model analysis: {str(e)}")
        return 0.0


def _analyze_with_keywords(text: str) -> float:
    """
    Fallback keyword-based bias detection
    """
    # Simple keyword-based detection as last resort
    problematic_keywords = [
        # Add appropriate keywords based on your use case
        # This is a very basic implementation
        'hate', 'kill', 'die', 'stupid', 'idiot', 'moron',
        'racist', 'sexist', 'discrimination'
    ]

    text_lower = text.lower()
    keyword_count = sum(
        1 for keyword in problematic_keywords if keyword in text_lower)

    # Simple scoring based on keyword density
    word_count = len(text.split())
    if word_count == 0:
        return 0.0

    keyword_density = keyword_count / word_count

    # Scale to 0-1 range
    # Multiply by 5 to amplify signal
    bias_score = min(1.0, keyword_density * 5.0)

    return float(bias_score)


def analyze_bias_categories(text: str) -> dict:
    """
    Analyze text for specific categories of bias

    Returns:
        Dictionary with bias scores for different categories
    """
    if not text or not text.strip():
        return {}

    try:
        # This is a simplified implementation
        # In production, you might use specialized models for each category

        overall_bias = score_bias(text)

        return {
            "overall_toxicity": overall_bias or 0.0,
            "hate_speech": _detect_hate_speech(text),
            "offensive_language": _detect_offensive_language(text),
            "racial_bias": _detect_racial_bias(text),
            "gender_bias": _detect_gender_bias(text),
            "bias_score": overall_bias or 0.0
        }

    except Exception as e:
        logger.error(f"Error in category analysis: {str(e)}")
        return {}


def analyze_bias_with_details(text: str) -> dict:
    """
    Analyze text for bias with detailed word-level information

    Returns:
        Dictionary with bias analysis including highlighted words and categories
    """
    if not text or not text.strip():
        return {}

    try:
        # Get category analysis
        categories = analyze_bias_categories(text)

        # Find problematic words and phrases
        problematic_words = _find_problematic_words(text)

        # Analyze line by line for context
        lines = text.split('\n')
        line_analysis = []

        for i, line_content in enumerate(lines):
            if line_content.strip():
                line_bias = _analyze_line_bias(line_content)
                if line_bias['score'] > 0.1:  # Only include lines with significant bias
                    line_analysis.append({
                        'line_number': i + 1,
                        'text': line_content.strip(),
                        'bias_score': line_bias['score'],
                        'categories': line_bias['categories'],
                        'problematic_words': line_bias['words']
                    })

        return {
            'overall_analysis': categories,
            'problematic_words': problematic_words,
            'line_analysis': line_analysis,
            'total_lines': len([l for l in lines if l.strip()]),
            'problematic_lines': len(line_analysis)
        }

    except Exception as e:
        logger.error(f"Error in detailed bias analysis: {str(e)}")
        return {}


def _detect_hate_speech(text: str) -> float:
    """
    Detect hate speech specifically
    """
    # Simplified implementation - in production, use specialized models
    hate_keywords = ['hate', 'racist', 'sexist',
                     'homophobic', 'discrimination']
    text_lower = text.lower()

    hate_count = sum(1 for keyword in hate_keywords if keyword in text_lower)
    word_count = len(text.split())

    if word_count == 0:
        return 0.0

    return min(1.0, (hate_count / word_count) * 10.0)


def _detect_offensive_language(text: str) -> float:
    """
    Detect offensive language
    """
    # Simplified implementation
    offensive_patterns = ['stupid', 'idiot', 'moron', 'dumb', 'loser']
    text_lower = text.lower()

    offensive_count = sum(
        1 for pattern in offensive_patterns if pattern in text_lower)
    word_count = len(text.split())

    if word_count == 0:
        return 0.0

    return min(1.0, (offensive_count / word_count) * 8.0)


def _detect_racial_bias(text: str) -> float:
    """
    Detect racial bias and discriminatory language
    """
    racial_keywords = ['racist', 'race', 'color', 'ethnic',
                       'minority', 'white', 'black', 'asian', 'hispanic']
    text_lower = text.lower()

    racial_count = sum(
        1 for keyword in racial_keywords if keyword in text_lower)
    word_count = len(text.split())

    if word_count == 0:
        return 0.0

    return min(1.0, (racial_count / word_count) * 6.0)


def _detect_gender_bias(text: str) -> float:
    """
    Detect gender bias and sexist language
    """
    gender_keywords = ['sexist', 'gender', 'male', 'female',
                       'man', 'woman', 'boy', 'girl', 'masculine', 'feminine']
    text_lower = text.lower()

    gender_count = sum(
        1 for keyword in gender_keywords if keyword in text_lower)
    word_count = len(text.split())

    if word_count == 0:
        return 0.0

    return min(1.0, (gender_count / word_count) * 6.0)


def _find_problematic_words(text: str) -> list:
    """
    Find and categorize problematic words in the text
    """
    problematic_words = []
    # Define word categories with their bias types
    word_categories = {
        'hate_speech': ['hate', 'racist', 'sexist', 'homophobic',
                        'discrimination'],
        'offensive': ['stupid', 'idiot', 'moron', 'dumb', 'loser',
                      'pathetic'],
        'racial': ['race', 'color', 'ethnic', 'minority'],
        'gender': ['sexist', 'gender', 'masculine', 'feminine']
    }

    words = text.split()
    for i, word in enumerate(words):
        word_lower = word.lower().strip('.,!?;:"')
        for category, keywords in word_categories.items():
            if word_lower in keywords:
                problematic_words.append({
                    'word': word,
                    'position': i,
                    'category': category,
                    'severity': 'high' if category == 'hate_speech' else 'medium'
                })

    return problematic_words


def _analyze_line_bias(line: str) -> dict:
    """
    Analyze a single line for bias content
    """
    line_lower = line.lower()
    categories = []
    words = []
    score = 0.0

    # Check for different bias types
    if any(word in line_lower for word in ['hate', 'racist', 'sexist']):
        categories.append('hate_speech')
        score += 0.8

    if any(word in line_lower for word in ['stupid', 'idiot', 'moron']):
        categories.append('offensive')
        score += 0.6

    if any(word in line_lower for word in ['race', 'color', 'ethnic']):
        categories.append('racial')
        score += 0.4

    if any(word in line_lower for word in ['gender', 'sexist', 'masculine', 'feminine']):
        categories.append('gender')
        score += 0.4

    # Find specific problematic words in this line
    line_words = line.split()
    for word in line_words:
        word_lower = word.lower().strip('.,!?;:"')
        if word_lower in ['hate', 'racist', 'sexist', 'stupid', 'idiot', 'moron']:
            words.append({
                'word': word,
                'category': 'hate_speech' if word_lower in ['hate', 'racist', 'sexist'] else 'offensive'
            })

    return {
        'score': min(1.0, score),
        'categories': categories,
        'words': words
    }
