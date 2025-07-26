from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import os

from config import Config
from models import get_db, create_tables, Conversation, Analysis
from mistral_client import MistralClient

# Create database tables
create_tables()

app = FastAPI(title="Jarvis Backend", description="AI-powered media analysis platform")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Mistral client
mistral_client = MistralClient()

@app.get("/")
def read_root():
    return {"message": "Jarvis Backend API", "status": "running"}

@app.get("/conversations")
def get_conversations(db: Session = Depends(get_db)):
    """Get all conversations"""
    conversations = db.query(Conversation).all()
    return conversations

@app.post("/conversations")
def create_conversation(title: str = "New Conversation", db: Session = Depends(get_db)):
    """Create a new conversation"""
    conversation = Conversation(title=title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

@app.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Get a specific conversation with its analyses"""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@app.post("/analyze")
async def analyze_media(
    conversation_id: int = Form(...),
    media_url: str = Form(...),
    media_type: str = Form(...),  # "video" or "image"
    db: Session = Depends(get_db)
):
    """Analyze media using Mistral AI"""
    try:
        # Create analysis record
        analysis = Analysis(
            conversation_id=conversation_id,
            media_url=media_url,
            media_type=media_type
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        # For now, we'll create a mock analysis
        # In a real implementation, you'd process the media here
        if media_type == "video":
            # Mock video analysis
            mock_transcript = "This is a sample transcript of the video content."
            insights = await mistral_client.analyze_transcript(mock_transcript)
            
            analysis.transcription = mock_transcript
            analysis.topics = insights.get("topics", [])
            analysis.concepts = insights.get("concepts", [])
            analysis.insights = insights
            
        elif media_type == "image":
            # Mock image analysis
            mock_description = "This is a sample description of the image content."
            insights = await mistral_client.analyze_image_description(mock_description)
            
            analysis.visual_elements = insights.get("visual_elements", [])
            analysis.insights = insights
        
        db.commit()
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_with_jarvis(
    conversation_id: int = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    """Chat with Jarvis about analyzed content"""
    try:
        # Get conversation context
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Create context from previous analyses
        context = ""
        for analysis in conversation.analyses:
            if analysis.transcription:
                context += f"Video content: {analysis.transcription}\n"
            if analysis.insights:
                context += f"Analysis: {json.dumps(analysis.insights)}\n"
        
        # Send to Mistral with context
        full_prompt = f"""
        Context from previous analyses:
        {context}
        
        User question: {message}
        
        Please provide a helpful response based on the analyzed content.
        """
        
        messages = [{"role": "user", "content": full_prompt}]
        response = await mistral_client.chat_completion(messages)
        
        return {
            "response": response.get("choices", [{}])[0].get("message", {}).get("content", "No response"),
            "conversation_id": conversation_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 