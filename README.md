# FluentIQ – AI-Powered Communication Feedback Platform

FluentIQ is a full-stack AI-powered web platform that evaluates grammar, fluency, politeness, and body language in presentation videos, providing comprehensive feedback to enhance communication skills.

## System Architecture

```
Next.js Frontend (Port 3000)
        ↓
Django REST API (Port 8000)
        ↓
Celery Workers (Async Processing)
        ↓
PostgreSQL Database + Redis Queue
        ↓
AI Models (Whisper, LanguageTool, OpenCV)
```

## Tech Stack

**Frontend:** Next.js 14 + TypeScript + Tailwind CSS (Coming Soon)
**Backend:** Django REST Framework + PostgreSQL + Celery + Redis
**NLP:** Whisper, LanguageTool, NLTK, OpenCV

## Installation

### Backend Setup

1. Navigate to backend:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Setup PostgreSQL and create database:
```bash
createdb fluentiq
```

5. Configure environment:
```bash
cp .env.example .env
# Edit .env with your credentials
```

6. Run migrations:
```bash
python manage.py migrate
```

7. Start Redis:
```bash
redis-server
```

8. Start Celery worker (new terminal):
```bash
celery -A fluentiq worker -l info
```

9. Start Django server:
```bash
python manage.py runserver
```

### Docker Setup (Recommended)

```bash
cd backend
docker-compose up --build
```

## Features

### Backend (Django REST Framework)
- RESTful API architecture
- Asynchronous video processing with Celery
- PostgreSQL database for data persistence
- Redis for task queue and caching
- User authentication and authorization
- Progress tracking over time

### AI Analysis Modules

**1. Video Processing**
- Asynchronous upload and processing
- Audio extraction from video
- Support for multiple formats (MP4, AVI, MOV, MKV)

**2. Speech-to-Text**
- Whisper AI for accurate transcription
- Multi-language support

**3. NLP Feedback Engine**
- Grammar analysis using LanguageTool
- Fluency analysis (filler words, repetitions)
- Politeness analysis (tone, formality)
- Body language analysis using OpenCV

**4. Scoring System**
- Grammar Score (0-100)
- Fluency Score (0-100)
- Politeness Score (0-100)
- Body Language Score (0-100)
- Overall Communication Score
- Detailed feedback with suggestions

**5. API Endpoints**
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/analyses/` - Upload video
- `GET /api/analyses/` - List analyses
- `GET /api/analyses/{id}/` - Get analysis details
- `GET /api/analyses/progress/` - Track improvement

## Design Decisions

- **Django REST Framework** - Robust, scalable API development
- **PostgreSQL** - Reliable relational database for production
- **Celery + Redis** - Asynchronous task processing for video analysis
- **Docker** - Containerization for consistent deployment
- **Modular architecture** - Separation of concerns for maintainability
- **Session-based auth** - Secure authentication system
- **Whisper AI** - State-of-the-art speech recognition
- **LanguageTool** - Comprehensive grammar checking
- **OpenCV** - Computer vision for body language analysis

## Storage

- **PostgreSQL** - User data, analysis results, and metadata
- **File Storage** - Videos stored in media directory
- **Redis** - Task queue and caching
- **Historical Data** - All analyses saved for progress tracking

## API Response Format

```json
{
  "id": 1,
  "status": "completed",
  "transcript": "Full transcription text...",
  "grammar_score": 82.5,
  "fluency_score": 76.3,
  "politeness_score": 88.0,
  "body_language_score": 75.5,
  "overall_score": 80.6,
  "detailed_feedback": [
    {
      "category": "Grammar",
      "score": 82,
      "status": "good",
      "summary": "Found 3 grammatical errors.",
      "suggestions": ["Review sentence structure", "Use grammar tools"]
    }
  ],
  "video_stats": {
    "eye_contact_percentage": 75.5,
    "hand_usage_percentage": 65.0
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Deployment

See [backend/README.md](backend/README.md) for detailed deployment instructions.

## Project Structure

```
FluentIQ/
├── backend/
│   ├── fluentiq/          # Django project settings
│   ├── api/               # REST API app
│   ├── core/              # Core models
│   ├── media/             # Uploaded videos
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/              # Legacy HTML (to be replaced with Next.js)
└── README.md
```
