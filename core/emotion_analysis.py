from transformers import pipeline

# Load a sentiment-analysis pipeline
# This will download the model the first time it's used
classifier = pipeline("sentiment-analysis")

def analyze_mood(text):
    """
    Uses a pretrained model to analyze the sentiment of a text.
    Returns a classification such as POSITIVE or NEGATIVE with a confidence score.
    """
    try:
        result = classifier(text)[0]
        label = result['label'].lower()  # e.g., 'positive', 'negative'
        score = round(result['score'], 2)
        return {
            "mood": label,
            "confidence": score,
            "original_text": text
        }
    except Exception as e:
        return {
            "error": str(e),
            "original_text": text
        }
