# FluentIQ – AI-Powered Communication Feedback Platform

FluentIQ is a full-stack AI-powered web platform that evaluates grammar, fluency, politeness, and body language in presentation videos, providing comprehensive feedback to enhance communication skills.

## 🏗️ Architecture

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

## 🚀 Tech Stack

### Backend
- **Django REST Framework** - RESTful API
- **PostgreSQL** - Relational database
- **Celery** - Asynchronous task queue
- **Redis** - Message broker & caching
- **Whisper** - Speech-to-text transcription
- **LanguageTool** - Grammar analysis
- **OpenCV** - Video analysis for body language
- **NLTK** - Natural language processing

### Frontend (Coming Soon)
- **Next.js 14** - React framework
- **Tailwind CSS** - Styling
- **TypeScript** - Type safety
- **Axios** - API client

## 📦 Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Option 1: Docker (Recommended)

```bash
cd backend
docker-compose up --build
```

### Option 2: Manual Setup

1. **Create virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup PostgreSQL**
```bash
createdb fluentiq
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Start Redis**
```bash
redis-server
```

8. **Start Celery worker** (in new terminal)
```bash
celery -A fluentiq worker -l info
```

9. **Start Django server**
```bash
python manage.py runserver
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout

### User
- `GET /api/users/me/` - Get current user

### Analysis
- `GET /api/analyses/` - List all analyses
- `POST /api/analyses/` - Upload video for analysis
- `GET /api/analyses/{id}/` - Get specific analysis
- `GET /api/analyses/progress/` - Get user progress over time

## 📊 Features

### 1. Video Upload & Processing
- Asynchronous video processing with Celery
- Support for MP4, AVI, MOV, MKV formats
- Real-time status updates

### 2. AI-Powered Analysis
- **Grammar Analysis**: Detects errors using LanguageTool
- **Fluency Analysis**: Identifies filler words and repetitions
- **Politeness Analysis**: Evaluates tone and formality
- **Body Language**: Analyzes eye contact and facial expressions

### 3. Scoring System
- Individual scores for each category (0-100)
- Overall communication score
- Detailed feedback with actionable suggestions

### 4. Progress Tracking
- Historical analysis data
- Improvement trends over time
- Visual progress charts

## 🗄️ Database Schema

### User Model
- email (unique)
- username
- password (hashed)
- created_at, updated_at

### Analysis Model
- user (ForeignKey)
- video (FileField)
- status (pending/processing/completed/failed)
- transcript (TextField)
- scores (grammar, fluency, politeness, body_language, overall)
- detailed_feedback (JSONField)
- video_stats (JSONField)
- timestamps

## 🔧 Configuration

### Environment Variables
```env
SECRET_KEY=your-django-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,yourdomain.com
DB_NAME=fluentiq
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=http://localhost:3000
```

## 🚀 Deployment

### Render Deployment

1. **Create PostgreSQL database** on Render
2. **Create Redis instance** on Render
3. **Create Web Service** for Django
   - Build Command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
   - Start Command: `gunicorn fluentiq.wsgi:application`
4. **Create Background Worker** for Celery
   - Start Command: `celery -A fluentiq worker -l info`

### Environment Variables on Render
- Set all variables from `.env.example`
- Add `DATABASE_URL` from PostgreSQL service
- Add `REDIS_URL` from Redis service

## 📈 Performance Optimizations

- **Asynchronous Processing**: Celery handles video processing in background
- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: Redis caching for frequently accessed data
- **Static Files**: WhiteNoise for efficient static file serving
- **Connection Pooling**: PostgreSQL connection pooling

## 🔒 Security Features

- Password hashing with Django's built-in system
- CSRF protection
- CORS configuration
- SQL injection prevention (Django ORM)
- File upload validation
- Session-based authentication

## 📝 Development

### Run tests
```bash
python manage.py test
```

### Create migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Access admin panel
```
http://localhost:8000/admin
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

MIT License

## 👨‍💻 Author

Uday Gundu - [GitHub](https://github.com/Uday1017)

## 🙏 Acknowledgments

- OpenAI Whisper for speech recognition
- LanguageTool for grammar checking
- Django & DRF community
