import cv2
import numpy as np
from collections import Counter

try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    MEDIAPIPE_AVAILABLE = True
except:
    MEDIAPIPE_AVAILABLE = False

def analyze_video_nonverbal(video_path: str) -> dict:
    if not MEDIAPIPE_AVAILABLE:
        return {
            "face_presence": 0,
            "eye_contact_percentage": 0,
            "hand_usage_percentage": 0,
            "hand_movements": 0,
            "smile_percentage": 0,
            "dominant_expression": "unknown",
            "total_frames_analyzed": 0
        }
    
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Sample every 15 frames for performance
    sample_rate = 15
    
    face_detected_frames = 0
    eye_contact_frames = 0
    hand_detected_frames = 0
    hand_movement_count = 0
    smile_frames = 0
    
    # Use Haar Cascade for face detection (simpler, no mediapipe dependency)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
    
    prev_frame_gray = None
    
    frame_count = 0
    sampled_frames = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % sample_rate != 0:
            frame_count += 1
            continue
        
        sampled_frames += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Face detection
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) > 0:
            face_detected_frames += 1
            
            for (x, y, w, h) in faces:
                roi_gray = gray[y:y+h, x:x+w]
                
                # Eye detection (proxy for eye contact)
                eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 5)
                if len(eyes) >= 2:
                    eye_contact_frames += 1
                
                # Smile detection
                smiles = smile_cascade.detectMultiScale(roi_gray, 1.8, 20)
                if len(smiles) > 0:
                    smile_frames += 1
        
        # Hand/movement detection using frame difference
        if prev_frame_gray is not None:
            frame_diff = cv2.absdiff(prev_frame_gray, gray)
            _, thresh = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)
            movement_pixels = np.sum(thresh) / 255
            
            # Significant movement detected
            if movement_pixels > 50000:
                hand_movement_count += 1
                hand_detected_frames += 1
        
        prev_frame_gray = gray.copy()
        frame_count += 1
    
    cap.release()
    
    # Calculate percentages
    face_presence = (face_detected_frames / sampled_frames * 100) if sampled_frames > 0 else 0
    eye_contact_pct = (eye_contact_frames / face_detected_frames * 100) if face_detected_frames > 0 else 0
    hand_usage_pct = (hand_detected_frames / sampled_frames * 100) if sampled_frames > 0 else 0
    smile_pct = (smile_frames / face_detected_frames * 100) if face_detected_frames > 0 else 0
    
    # Determine engagement level
    if smile_pct > 30:
        expression = "engaging"
    elif smile_pct > 10:
        expression = "neutral"
    else:
        expression = "serious"
    
    return {
        "face_presence": round(face_presence, 1),
        "eye_contact_percentage": round(eye_contact_pct, 1),
        "hand_usage_percentage": round(hand_usage_pct, 1),
        "hand_movements": hand_movement_count,
        "smile_percentage": round(smile_pct, 1),
        "dominant_expression": expression,
        "total_frames_analyzed": sampled_frames
    }
