import language_tool_python
import re
import nltk
from collections import Counter

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

tool = language_tool_python.LanguageTool('en-US')

FILLER_WORDS = ['um', 'uh', 'like', 'you know', 'so', 'actually', 'basically', 'literally']
POLITE_WORDS = ['please', 'thank', 'appreciate', 'kindly', 'would', 'could', 'may']
IMPOLITE_PATTERNS = ['must', 'have to', 'need to', 'should']

def analyze_communication(transcript: str) -> dict:
    grammar_errors = tool.check(transcript)
    sentences = nltk.sent_tokenize(transcript)
    words = transcript.lower().split()
    
    filler_count = sum(words.count(filler) for filler in FILLER_WORDS)
    word_repetitions = [word for word, count in Counter(words).items() if count > 3 and len(word) > 3]
    
    polite_count = sum(1 for word in POLITE_WORDS if word in transcript.lower())
    impolite_count = sum(1 for pattern in IMPOLITE_PATTERNS if pattern in transcript.lower())
    
    return {
        "grammar_errors": len(grammar_errors),
        "grammar_details": [{"message": e.message, "context": e.context} for e in grammar_errors[:5]],
        "total_words": len(words),
        "total_sentences": len(sentences),
        "filler_count": filler_count,
        "repetitions": word_repetitions[:5],
        "polite_count": polite_count,
        "impolite_count": impolite_count
    }
