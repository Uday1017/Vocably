# Vocably - AI Communication Coach

Vocably allows users to upload presentation videos and receive structured feedback on communication quality including grammar, fluency, and politeness.

## System Architecture

```
Frontend (Upload UI)
        ↓
FastAPI Backend
        ↓
Audio Extraction + Transcription
        ↓
NLP Feedback Engine
        ↓
Scoring + Response Generation
        ↓
Results Page (Frontend)
```

## Tech Stack

**Frontend:** HTML + TailwindCSS
**Backend:** FastAPI (Python)
**NLP:** Whisper, LanguageTool, NLTK

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

3. Open browser:
```
http://localhost:8000
```

## Features

### Frontend
- Video upload interface
- Real-time processing feedback
- Score visualization
- Detailed feedback display

### Backend Modules

**1. Video Processing Module**
- Receives uploaded video
- Extracts audio from video

**2. Speech-to-Text Module**
- Converts audio to text using Whisper
- Generates transcript

**3. NLP Feedback Engine**
- Grammar analysis (sentence structure, errors)
- Fluency analysis (filler words, repetition)
- Politeness analysis (tone, formality)

**4. Scoring Engine**
- Grammar Score (0-100)
- Fluency Score (0-100)
- Politeness Score (0-100)
- Improvement suggestions

**5. API Layer**
- `POST /analyze-video` - Main analysis endpoint

## Design Decisions

- **FastAPI** chosen for quick API development and async support
- **TailwindCSS** used for fast, responsive UI styling
- **Pipeline architecture** separates processing steps for maintainability
- **Modular backend** allows easy extension and testing
- **Real-time processing** - no database needed for MVP
- **Whisper** for accurate speech recognition
- **LanguageTool** for comprehensive grammar checking

## Storage

Currently uses real-time processing without permanent storage. Videos and audio files are deleted after analysis. A database (SQLite/PostgreSQL) can be added to store user history.

## API Response Format

```json
{
  "transcript": "Full transcription text...",
  "grammar_score": 82,
  "fluency_score": 76,
  "politeness_score": 88,
  "feedback": [
    "Grammar: Found 3 errors. Review sentence structure.",
    "Fluency: Reduce filler words (found 5). Practice pausing instead."
  ]
}
```
