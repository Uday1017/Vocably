def generate_scores(analysis: dict, transcript: str, video_analysis: dict = None) -> dict:
    total_words = analysis["total_words"]
    
    grammar_score = max(0, 100 - (analysis["grammar_errors"] * 5))
    filler_penalty = (analysis["filler_count"] / total_words * 100) * 2 if total_words > 0 else 0
    repetition_penalty = len(analysis["repetitions"]) * 3
    fluency_score = max(0, 100 - filler_penalty - repetition_penalty)
    polite_boost = min(20, analysis["polite_count"] * 4)
    impolite_penalty = analysis["impolite_count"] * 5
    politeness_score = max(0, min(100, 70 + polite_boost - impolite_penalty))
    
    detailed_feedback = []
    resources = []
    
    # Grammar Feedback
    if grammar_score < 80:
        grammar_issues = []
        if analysis["grammar_details"]:
            for detail in analysis["grammar_details"][:3]:
                grammar_issues.append(f"• {detail['message']}")
        
        detailed_feedback.append({
            "category": "Grammar",
            "score": round(grammar_score),
            "status": "needs_improvement",
            "summary": f"Found {analysis['grammar_errors']} grammatical errors in your presentation.",
            "issues": grammar_issues if grammar_issues else ["• Review sentence structure and verb tenses"],
            "suggestions": [
                "Proofread your script before presenting",
                "Use grammar checking tools like Grammarly",
                "Practice speaking in complete sentences",
                "Record yourself and review for errors"
            ]
        })
        resources.append({
            "category": "Grammar",
            "items": [
                {"title": "English Grammar Basics", "url": "https://www.youtube.com/results?search_query=english+grammar+for+presentations", "type": "YouTube"},
                {"title": "Common Grammar Mistakes", "url": "https://www.grammarly.com/blog/common-grammar-mistakes/", "type": "Blog"},
                {"title": "Business English Grammar", "url": "https://www.coursera.org/courses?query=business%20english", "type": "Course"}
            ]
        })
    elif grammar_score >= 90:
        detailed_feedback.append({
            "category": "Grammar",
            "score": round(grammar_score),
            "status": "excellent",
            "summary": "Your grammar is excellent! Very few errors detected.",
            "issues": [],
            "suggestions": ["Maintain this level of grammatical accuracy"]
        })
    else:
        detailed_feedback.append({
            "category": "Grammar",
            "score": round(grammar_score),
            "status": "good",
            "summary": "Good grammar overall with minor improvements needed.",
            "issues": [f"• {analysis['grammar_details'][0]['message']}"] if analysis["grammar_details"] else [],
            "suggestions": ["Review and polish your sentence structure"]
        })
    
    # Fluency Feedback
    if fluency_score < 80:
        fluency_issues = []
        if analysis["filler_count"] > 0:
            fluency_issues.append(f"• Used {analysis['filler_count']} filler words (um, uh, like, etc.)")
        if analysis["repetitions"]:
            fluency_issues.append(f"• Repeated words: {', '.join(analysis['repetitions'][:3])}")
        
        detailed_feedback.append({
            "category": "Fluency",
            "score": round(fluency_score),
            "status": "needs_improvement",
            "summary": "Your speech flow needs improvement to sound more natural and confident.",
            "issues": fluency_issues,
            "suggestions": [
                "Practice pausing instead of using filler words",
                "Slow down your speaking pace",
                "Prepare and rehearse key points",
                "Use breathing techniques to maintain flow",
                "Expand your vocabulary to avoid repetition"
            ]
        })
        resources.append({
            "category": "Fluency",
            "items": [
                {"title": "How to Stop Saying Um and Uh", "url": "https://www.youtube.com/results?search_query=how+to+stop+saying+um+and+uh", "type": "YouTube"},
                {"title": "Public Speaking Fluency Tips", "url": "https://www.toastmasters.org/resources/public-speaking-tips", "type": "Blog"},
                {"title": "Presentation Skills Course", "url": "https://www.coursera.org/courses?query=presentation%20skills", "type": "Course"}
            ]
        })
    elif fluency_score >= 90:
        detailed_feedback.append({
            "category": "Fluency",
            "score": round(fluency_score),
            "status": "excellent",
            "summary": "Excellent fluency! Your speech flows naturally and confidently.",
            "issues": [],
            "suggestions": ["Keep up the great work!"]
        })
    else:
        detailed_feedback.append({
            "category": "Fluency",
            "score": round(fluency_score),
            "status": "good",
            "summary": "Good fluency with room for minor improvements.",
            "issues": [f"• Minimize filler words ({analysis['filler_count']} detected)"] if analysis["filler_count"] > 0 else [],
            "suggestions": ["Practice to reduce hesitations"]
        })
    
    # Politeness Feedback
    if politeness_score < 80:
        detailed_feedback.append({
            "category": "Politeness",
            "score": round(politeness_score),
            "status": "needs_improvement",
            "summary": "Your tone could be more courteous and professional.",
            "issues": [
                f"• Limited use of polite expressions ({analysis['polite_count']} detected)",
                f"• Used {analysis['impolite_count']} direct/commanding phrases"
            ],
            "suggestions": [
                "Use 'please', 'thank you', 'I appreciate' more often",
                "Replace 'must' with 'could you please'",
                "Use 'would you' instead of 'you should'",
                "Frame requests as questions, not commands",
                "Show gratitude to your audience"
            ]
        })
        resources.append({
            "category": "Politeness",
            "items": [
                {"title": "Professional Communication Skills", "url": "https://www.youtube.com/results?search_query=professional+communication+skills", "type": "YouTube"},
                {"title": "Business Etiquette Guide", "url": "https://www.indeed.com/career-advice/career-development/business-etiquette", "type": "Blog"},
                {"title": "Effective Communication Course", "url": "https://www.linkedin.com/learning/topics/communication", "type": "Course"}
            ]
        })
    elif politeness_score >= 90:
        detailed_feedback.append({
            "category": "Politeness",
            "score": round(politeness_score),
            "status": "excellent",
            "summary": "Excellent professional tone and courteous language!",
            "issues": [],
            "suggestions": ["Your communication style is very professional"]
        })
    else:
        detailed_feedback.append({
            "category": "Politeness",
            "score": round(politeness_score),
            "status": "good",
            "summary": "Good professional tone with minor enhancements possible.",
            "issues": [],
            "suggestions": ["Consider adding more courteous expressions"]
        })
    
    # Overall Summary
    avg_score = (grammar_score + fluency_score + politeness_score) / 3
    
    # Add video analysis feedback if available
    if video_analysis:
        eye_contact_score = video_analysis["eye_contact_percentage"]
        hand_usage_score = min(100, video_analysis["hand_usage_percentage"] * 1.5)
        expression_score = 90 if video_analysis["dominant_expression"] == "engaging" else 70 if video_analysis["dominant_expression"] == "neutral" else 50
        
        body_language_score = (eye_contact_score + hand_usage_score + expression_score) / 3
        
        # Body Language Feedback
        body_issues = []
        if eye_contact_score < 60:
            body_issues.append(f"• Eye contact: {eye_contact_score:.0f}% - Look at the camera more often")
        if hand_usage_score < 40:
            body_issues.append(f"• Hand gestures: Limited usage - Use hands to emphasize points")
        if video_analysis["smile_percentage"] < 10:
            body_issues.append(f"• Facial expression: Too serious - Smile more to appear approachable")
        
        body_suggestions = []
        if eye_contact_score < 70:
            body_suggestions.extend([
                "Practice looking directly at the camera lens",
                "Imagine you're talking to a friend through the camera",
                "Avoid reading from notes constantly"
            ])
        if hand_usage_score < 50:
            body_suggestions.extend([
                "Use hand gestures to emphasize key points",
                "Keep hands visible and avoid crossing arms",
                "Practice natural gestures that match your words"
            ])
        if video_analysis["dominant_expression"] != "engaging":
            body_suggestions.extend([
                "Smile naturally when appropriate",
                "Show enthusiasm through facial expressions",
                "Relax your face to appear more approachable"
            ])
        
        if body_language_score < 80:
            detailed_feedback.append({
                "category": "Body Language",
                "score": round(body_language_score),
                "status": "excellent" if body_language_score >= 85 else "good" if body_language_score >= 70 else "needs_improvement",
                "summary": "Your non-verbal communication impacts how your message is received.",
                "issues": body_issues if body_issues else [],
                "suggestions": body_suggestions if body_suggestions else ["Maintain good body language"]
            })
            
            resources.append({
                "category": "Body Language",
                "items": [
                    {"title": "Body Language for Presentations", "url": "https://www.youtube.com/results?search_query=body+language+for+presentations", "type": "YouTube"},
                    {"title": "Eye Contact Tips", "url": "https://www.youtube.com/results?search_query=eye+contact+presentation+tips", "type": "YouTube"},
                    {"title": "Hand Gestures Guide", "url": "https://www.scienceofpeople.com/hand-gestures/", "type": "Blog"}
                ]
            })
        else:
            detailed_feedback.append({
                "category": "Body Language",
                "score": round(body_language_score),
                "status": "excellent" if body_language_score >= 85 else "good",
                "summary": "Great non-verbal communication! Your body language supports your message.",
                "issues": [],
                "suggestions": ["Keep up the excellent body language"]
            })
        
        avg_score = (grammar_score + fluency_score + politeness_score + body_language_score) / 4
    
    if avg_score >= 85:
        overall_message = "Outstanding presentation! You demonstrate strong communication skills."
    elif avg_score >= 70:
        overall_message = "Good presentation with some areas for improvement."
    else:
        overall_message = "Your presentation needs work. Focus on the suggestions below."
    
    return {
        "grammar_score": round(grammar_score),
        "fluency_score": round(fluency_score),
        "politeness_score": round(politeness_score),
        "body_language_score": round(body_language_score) if video_analysis else None,
        "overall_score": round(avg_score),
        "overall_message": overall_message,
        "detailed_feedback": detailed_feedback,
        "resources": resources,
        "stats": {
            "total_words": total_words,
            "total_sentences": analysis["total_sentences"],
            "grammar_errors": analysis["grammar_errors"],
            "filler_words": analysis["filler_count"],
            "polite_expressions": analysis["polite_count"]
        },
        "video_stats": video_analysis if video_analysis else None
    }
