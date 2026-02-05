"""
FastAPI Backend Server for Educational AI Platform
Handles API requests, LLM processing, and video generation
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict
import uuid
import asyncio
import logging
from pathlib import Path

from llm_engine import LLMEngine, check_system_ready
from animation_generator import AnimationGenerator
from config import SERVER_CONFIG, VIDEOS_DIR

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Educational AI Platform",
    description="AI-powered educational assistant with animated explanations",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (videos)
app.mount("/videos", StaticFiles(directory=str(VIDEOS_DIR)), name="videos")

# Initialize components
llm_engine = LLMEngine()
animation_generator = AnimationGenerator()

# Task storage for async video generation
video_tasks: Dict[str, Dict] = {}


# Request/Response Models
class QuestionRequest(BaseModel):
    question: str
    context: Optional[str] = None


class QuestionResponse(BaseModel):
    task_id: str
    answer: str
    topic: str
    status: str
    message: str


class TaskStatus(BaseModel):
    task_id: str
    status: str  # "processing", "completed", "failed"
    answer: Optional[str] = None
    video_url: Optional[str] = None
    error: Optional[str] = None


# API Endpoints

@app.get("/")
async def root():
    """Serve the main HTML page"""
    return FileResponse("index.html")


@app.get("/api/health")
async def health_check():
    """Check if the system is ready"""
    system_status = check_system_ready()
    
    return {
        "status": "healthy" if system_status["system_ready"] else "degraded",
        "ollama_running": system_status["ollama_running"],
        "model_available": system_status["model_available"],
        "model": llm_engine.model
    }


@app.post("/api/ask", response_model=QuestionResponse)
def ask_question(request: QuestionRequest, background_tasks: BackgroundTasks):
    """
    Process a question and generate answer + video
    """
    # Generate unique task ID
    task_id = str(uuid.uuid4())[:8]
    logger.info(f"Processing question: {request.question}")
    
    # Get answer from LLM
    try:
        response = llm_engine.generate_response(request.question, request.context)
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        raise HTTPException(status_code=500, detail="Internal LLM error")
    
    if response.get("error"):
        logger.error(f"LLM returned error: {response['answer']}")
        raise HTTPException(status_code=500, detail=response["answer"])
    
    logger.info(f"Answer generated for task {task_id}")
    logger.debug(f"Full answer: {response['answer']}")
    
    # Initialize task status
    video_tasks[task_id] = {
        "status": "processing",
        "answer": response["answer"],
        "topic": response["topic"],
        "video_url": None,
        "error": None
    }
    
    # Start video generation in background
    logger.info(f"Starting background video task for {task_id}")
    background_tasks.add_task(
        generate_video_task,
        task_id=task_id,
        topic=request.question,
        explanation=response["answer"],
        formulas=response.get("key_concepts", [])
    )
    
    return QuestionResponse(
        task_id=task_id,
        answer=response["answer"],
        topic=response["topic"],
        status="processing",
        message="Answer generated. Video is being created..."
    )


@app.get("/api/status/{task_id}", response_model=TaskStatus)
def get_task_status(task_id: str):
    """Check the status of a video generation task"""
    if task_id not in video_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = video_tasks[task_id]
    
    return TaskStatus(
        task_id=task_id,
        status=task["status"],
        answer=task.get("answer"),
        video_url=task.get("video_url"),
        error=task.get("error")
    )


@app.get("/api/models")
def list_models():
    """List available LLM models"""
    models = llm_engine.list_available_models()
    return {
        "current_model": llm_engine.model,
        "available_models": models
    }


@app.post("/api/switch-model/{model_name}")
def switch_model(model_name: str):
    """Switch to a different LLM model"""
    available = llm_engine.list_available_models()
    
    if model_name not in available:
        # Try to pull the model
        success = llm_engine.pull_model(model_name)
        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Model {model_name} not available and could not be downloaded"
            )
    
    llm_engine.model = model_name
    return {"message": f"Switched to model: {model_name}"}


# Background Tasks

def generate_video_task(
    task_id: str,
    topic: str,
    explanation: str,
    formulas: list
):
    """Background task to generate animation video"""
    try:
        # Extract formulas from explanation if not provided
        if not formulas:
            formulas = animation_generator.extract_formulas(explanation)
        
        # Generate video (this may take 10-30 seconds)
        video_path = animation_generator.generate_video(
            topic=topic,
            explanation=explanation,
            formulas=formulas,
            video_id=task_id
        )
        
        if video_path:
            # Update task status
            video_tasks[task_id]["status"] = "completed"
            video_tasks[task_id]["video_url"] = f"/videos/{task_id}.mp4"
            logger.info(f"Video task {task_id} completed successfully")
        else:
            video_tasks[task_id]["status"] = "failed"
            video_tasks[task_id]["error"] = "Failed to generate video"
            logger.error(f"Video task {task_id} failed: No video path returned")
            
    except Exception as e:
        video_tasks[task_id]["status"] = "failed"
        video_tasks[task_id]["error"] = str(e)
        logger.error(f"Video task {task_id} crashed: {e}")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Check system readiness on startup"""
    print("🚀 Starting Educational AI Platform...")
    
    system_status = check_system_ready()
    
    if not system_status["ollama_running"]:
        print("⚠️  WARNING: Ollama is not running!")
        print("   Please start Ollama: ollama serve")
    else:
        print("✅ Ollama is running")
    
    if not system_status["model_available"]:
        print(f"⚠️  WARNING: Model '{llm_engine.model}' not found")
        print(f"   Downloading {llm_engine.model}...")
        if llm_engine.pull_model(llm_engine.model):
            print(f"✅ Model downloaded successfully")
        else:
            print(f"❌ Failed to download model")
    else:
        print(f"✅ Model '{llm_engine.model}' is ready")
    
    print(f"\n🌐 Server running at http://localhost:{SERVER_CONFIG['port']}")
    print("📚 Ready to answer educational questions!\n")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host=SERVER_CONFIG["host"],
        port=SERVER_CONFIG["port"],
        reload=SERVER_CONFIG["reload"]
    )
