from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Response, Cookie, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
import os
import shutil
from pathlib import Path
from modules.video_processor import extract_audio
from modules.speech_to_text import transcribe_audio
from modules.nlp_engine import analyze_communication
from modules.scoring import generate_scores
from modules.video_analysis import analyze_video_nonverbal
from database import init_db, get_db, User, Analysis
from auth import create_access_token, get_current_user_id
from typing import Optional

app = FastAPI(title="Vocably API")

init_db()  # Initialize database

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def root():
    return FileResponse("frontend/index.html")

@app.get("/login")
async def login_page():
    return FileResponse("frontend/login.html")

@app.get("/signup")
async def signup_page():
    return FileResponse("frontend/signup.html")

@app.get("/dashboard")
async def dashboard_page():
    return FileResponse("frontend/dashboard.html")

@app.get("/upload")
async def upload_page():
    return FileResponse("frontend/upload.html")

@app.post("/api/signup")
async def signup(name: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(400, "Email already registered")
    
    user = User(name=name, email=email)
    user.set_password(password)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"user_id": user.id, "email": user.email})
    response = JSONResponse({"message": "User created successfully"})
    response.set_cookie(key="token", value=token, httponly=True, max_age=30*24*60*60)
    return response

@app.post("/api/login")
async def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.check_password(password):
        raise HTTPException(401, "Invalid credentials")
    
    token = create_access_token({"user_id": user.id, "email": user.email})
    response = JSONResponse({"message": "Login successful", "user": {"name": user.name, "email": user.email}})
    response.set_cookie(key="token", value=token, httponly=True, max_age=30*24*60*60)
    return response

@app.post("/api/logout")
async def logout():
    response = JSONResponse({"message": "Logged out"})
    response.delete_cookie(key="token")
    return response

@app.get("/api/me")
async def get_current_user(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return {"id": user.id, "name": user.name, "email": user.email}

@app.get("/api/analyses")
async def get_user_analyses(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    analyses = db.query(Analysis).filter(Analysis.user_id == user_id).order_by(Analysis.created_at.desc()).all()
    return [{"id": a.id, "filename": a.filename, "grammar_score": a.grammar_score, "fluency_score": a.fluency_score, 
             "politeness_score": a.politeness_score, "body_language_score": a.body_language_score, 
             "overall_score": a.overall_score, "created_at": a.created_at.isoformat()} for a in analyses]

@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.user_id == user_id).first()
    if not analysis:
        raise HTTPException(404, "Analysis not found")
    return {"id": analysis.id, "filename": analysis.filename, "transcript": analysis.transcript,
            "grammar_score": analysis.grammar_score, "fluency_score": analysis.fluency_score,
            "politeness_score": analysis.politeness_score, "body_language_score": analysis.body_language_score,
            "overall_score": analysis.overall_score, "created_at": analysis.created_at.isoformat()}

@app.get("/api/progress")
async def get_user_progress(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    analyses = db.query(Analysis).filter(Analysis.user_id == user_id).order_by(Analysis.created_at).all()
    
    if len(analyses) < 2:
        return {"has_progress": False, "message": "Need at least 2 analyses to show progress"}
    
    progress_data = {
        "has_progress": True,
        "total_analyses": len(analyses),
        "grammar": [a.grammar_score for a in analyses],
        "fluency": [a.fluency_score for a in analyses],
        "politeness": [a.politeness_score for a in analyses],
        "body_language": [a.body_language_score for a in analyses if a.body_language_score],
        "overall": [a.overall_score for a in analyses],
        "dates": [a.created_at.strftime("%b %d") for a in analyses],
        "improvement": {
            "grammar": round(analyses[-1].grammar_score - analyses[0].grammar_score, 1),
            "fluency": round(analyses[-1].fluency_score - analyses[0].fluency_score, 1),
            "politeness": round(analyses[-1].politeness_score - analyses[0].politeness_score, 1),
            "overall": round(analyses[-1].overall_score - analyses[0].overall_score, 1)
        }
    }
    return progress_data

@app.post("/analyze-video")
async def analyze_video(file: UploadFile = File(...), user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    if not file.filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
        raise HTTPException(400, "Invalid video format")
    
    video_path = UPLOAD_DIR / file.filename
    audio_path = UPLOAD_DIR / f"{Path(file.filename).stem}.wav"
    
    try:
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        video_analysis = analyze_video_nonverbal(str(video_path))
        extract_audio(str(video_path), str(audio_path))
        transcript = transcribe_audio(str(audio_path))
        analysis = analyze_communication(transcript)
        scores = generate_scores(analysis, transcript, video_analysis)
        
        # Save to database
        db_analysis = Analysis(
            user_id=user_id,
            filename=file.filename,
            transcript=transcript,
            grammar_score=scores["grammar_score"],
            fluency_score=scores["fluency_score"],
            politeness_score=scores["politeness_score"],
            body_language_score=scores["body_language_score"],
            overall_score=scores["overall_score"]
        )
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        
        os.remove(video_path)
        os.remove(audio_path)
        
        return {
            "analysis_id": db_analysis.id,
            "transcript": transcript,
            "grammar_score": scores["grammar_score"],
            "fluency_score": scores["fluency_score"],
            "politeness_score": scores["politeness_score"],
            "body_language_score": scores["body_language_score"],
            "overall_score": scores["overall_score"],
            "overall_message": scores["overall_message"],
            "detailed_feedback": scores["detailed_feedback"],
            "resources": scores["resources"],
            "stats": scores["stats"],
            "video_stats": scores["video_stats"]
        }
    
    except Exception as e:
        if video_path.exists():
            os.remove(video_path)
        if audio_path.exists():
            os.remove(audio_path)
        raise HTTPException(500, f"Processing error: {str(e)}")

@app.get("/results")
async def results_page():
    return FileResponse("frontend/results.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
