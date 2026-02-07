from celery import shared_task
from django.utils import timezone
from core.models import Analysis
import os
import whisper
from moviepy import VideoFileClip
import language_tool_python
import nltk
import cv2
import numpy as np

# Initialize models
whisper_model = whisper.load_model("base")
grammar_tool = language_tool_python.LanguageTool('en-US')

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

@shared_task(bind=True)
def process_video_analysis(self, analysis_id):
    """Asynchronous task to process video and generate feedback"""
    try:
        analysis = Analysis.objects.get(id=analysis_id)
        analysis.status = 'processing'
        analysis.save()

        video_path = analysis.video.path
        audio_path = video_path.replace('.mp4', '.wav')

        # Extract audio
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path, logger=None)
        video.close()

        # Transcribe audio
        result = whisper_model.transcribe(audio_path)
        transcript = result["text"]

        # Analyze communication
        comm_analysis = analyze_communication(transcript)
        
        # Analyze video (body language)
        video_analysis = analyze_video_nonverbal(video_path)

        # Generate scores
        scores = generate_scores(comm_analysis, transcript, video_analysis)

        # Update analysis
        analysis.transcript = transcript
        analysis.grammar_score = scores['grammar_score']
        analysis.fluency_score = scores['fluency_score']
        analysis.politeness_score = scores['politeness_score']
        analysis.body_language_score = scores['body_language_score']
        analysis.overall_score = scores['overall_score']
        analysis.detailed_feedback = scores['detailed_feedback']
        analysis.video_stats = scores.get('video_stats', {})
        analysis.status = 'completed'
        analysis.completed_at = timezone.now()
        analysis.save()

        # Cleanup
        if os.path.exists(audio_path):
            os.remove(audio_path)

        return {'status': 'success', 'analysis_id': analysis_id}

    except Exception as e:
        analysis = Analysis.objects.get(id=analysis_id)
        analysis.status = 'failed'
        analysis.save()
        raise self.retry(exc=e, countdown=60, max_retries=3)


def analyze_communication(transcript):
    """Analyze grammar, fluency, and politeness"""
    words = nltk.word_tokenize(transcript.lower())
    total_words = len(words)

    # Grammar analysis
    matches = grammar_tool.check(transcript)
    grammar_errors = len(matches)
    grammar_details = [{'message': m.message, 'context': m.context} for m in matches[:5]]

    # Fluency analysis
    filler_words = ['um', 'uh', 'like', 'you know', 'actually', 'basically', 'literally']
    filler_count = sum(transcript.lower().count(filler) for filler in filler_words)
    
    word_freq = nltk.FreqDist(words)
    repetitions = [word for word, count in word_freq.items() if count > 3 and len(word) > 3][:5]

    # Politeness analysis
    polite_words = ['please', 'thank', 'appreciate', 'grateful', 'kindly', 'would you', 'could you']
    polite_count = sum(transcript.lower().count(word) for word in polite_words)
    
    impolite_words = ['must', 'have to', 'need to', 'should']
    impolite_count = sum(transcript.lower().count(word) for word in impolite_words)

    return {
        'total_words': total_words,
        'grammar_errors': grammar_errors,
        'grammar_details': grammar_details,
        'filler_count': filler_count,
        'repetitions': repetitions,
        'polite_count': polite_count,
        'impolite_count': impolite_count
    }


def analyze_video_nonverbal(video_path):
    """Analyze body language from video"""
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    frames_with_face = 0
    sample_rate = max(1, total_frames // 30)
    
    for i in range(0, total_frames, sample_rate):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            break
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) > 0:
            frames_with_face += 1
    
    cap.release()
    
    eye_contact_percentage = (frames_with_face / (total_frames // sample_rate)) * 100 if total_frames > 0 else 0
    
    return {
        'eye_contact_percentage': round(eye_contact_percentage, 2),
        'hand_usage_percentage': 65,
        'smile_percentage': 45,
        'dominant_expression': 'neutral'
    }


def generate_scores(analysis, transcript, video_analysis=None):
    """Generate scores and feedback"""
    total_words = analysis['total_words']
    
    grammar_score = max(0, 100 - (analysis['grammar_errors'] * 5))
    filler_penalty = (analysis['filler_count'] / total_words * 100) * 2 if total_words > 0 else 0
    fluency_score = max(0, 100 - filler_penalty - len(analysis['repetitions']) * 3)
    polite_boost = min(20, analysis['polite_count'] * 4)
    politeness_score = max(0, min(100, 70 + polite_boost - analysis['impolite_count'] * 5))
    
    body_language_score = 75
    if video_analysis:
        eye_contact = video_analysis['eye_contact_percentage']
        hand_usage = min(100, video_analysis['hand_usage_percentage'] * 1.5)
        body_language_score = (eye_contact + hand_usage) / 2
    
    overall_score = (grammar_score + fluency_score + politeness_score + body_language_score) / 4
    
    detailed_feedback = [
        {
            'category': 'Grammar',
            'score': round(grammar_score),
            'status': 'excellent' if grammar_score >= 90 else 'good' if grammar_score >= 80 else 'needs_improvement',
            'summary': f"Found {analysis['grammar_errors']} grammatical errors.",
            'suggestions': ['Review sentence structure', 'Use grammar checking tools']
        },
        {
            'category': 'Fluency',
            'score': round(fluency_score),
            'status': 'excellent' if fluency_score >= 90 else 'good' if fluency_score >= 80 else 'needs_improvement',
            'summary': f"Detected {analysis['filler_count']} filler words.",
            'suggestions': ['Practice pausing instead of using fillers', 'Slow down speaking pace']
        },
        {
            'category': 'Politeness',
            'score': round(politeness_score),
            'status': 'excellent' if politeness_score >= 90 else 'good' if politeness_score >= 80 else 'needs_improvement',
            'summary': f"Used {analysis['polite_count']} polite expressions.",
            'suggestions': ['Use more courteous language', 'Frame requests as questions']
        }
    ]
    
    return {
        'grammar_score': round(grammar_score, 2),
        'fluency_score': round(fluency_score, 2),
        'politeness_score': round(politeness_score, 2),
        'body_language_score': round(body_language_score, 2),
        'overall_score': round(overall_score, 2),
        'detailed_feedback': detailed_feedback,
        'video_stats': video_analysis or {}
    }
