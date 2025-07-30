from textblob import TextBlob

def get_sentiment(text):
    """
    Analyzes sentiment of the given text.

    Returns:
        "Positive", "Negative", or "Neutral"
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0.2:
        return "Positive"
    elif polarity < -0.2:
        return "Negative"
    else:
        return "Neutral"
