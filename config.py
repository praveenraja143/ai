"""
Configuration settings for Educational AI Platform
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
VIDEOS_DIR = BASE_DIR / "videos"
TEMP_DIR = BASE_DIR / "temp"

# Create directories if they don't exist
VIDEOS_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# LLM Configuration
LLM_CONFIG = {
    "model": "mistral:latest",  # Match installed Ollama model
    "temperature": 0.5,
    "max_tokens": 500,
    "context_window": 2048,
}

# Gemini Configuration
GEMINI_CONFIG = {
    "api_key": os.environ.get("GEMINI_API_KEY", "AIzaSyC7XsUIXpTFiASVo7131Xo4zHWA2YuFBlY"),
    "model": "gemini-pro",
}

# Alternative models (user can switch)
AVAILABLE_MODELS = [
    "mistral",      # 7B - Fast and efficient
    "llama3",       # 8B - High quality
    "phi3",         # 3.8B - Lightweight
    "gemma:2b",     # 2B - Very fast
]

# Animation Configuration
ANIMATION_CONFIG = {
    "quality": "medium_quality",  # low_quality, medium_quality, high_quality, production_quality
    "fps": 30,
    "resolution": "720p",  # 480p, 720p, 1080p
    "background_color": "#0f0f23",
    "text_color": "#ffffff",
}

# Video quality presets
QUALITY_PRESETS = {
    "480p": {"width": 854, "height": 480},
    "720p": {"width": 1280, "height": 720},
    "1080p": {"width": 1920, "height": 1080},
}

# Server Configuration
SERVER_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "reload": False,  # Set to False in production
}

# Ollama Configuration
OLLAMA_CONFIG = {
    "base_url": "http://127.0.0.1:11434",
    "timeout": 120,  # seconds
}

# Educational Topics Templates
TOPIC_TEMPLATES = {
    "mathematics": ["theorem", "formula", "equation", "proof", "calculation"],
    "physics": ["law", "force", "motion", "energy", "wave"],
    "chemistry": ["reaction", "molecule", "element", "bond", "equation"],
    "computer_science": ["algorithm", "data structure", "complexity", "sorting"],
}

# System prompts for educational content
SYSTEM_PROMPT = """You are an expert educational AI assistant.
Explain concepts clearly and concisely for students.
Break down complex ideas into simple terms with examples.
Always provide: 
1. A clear definition
2. Key formulas/principles
3. A short example.
Keep the total response under 400 words.
"""

# Animation prompt template
ANIMATION_PROMPT_TEMPLATE = """Based on this educational content, create a visual animation script:

Topic: {topic}
Explanation: {explanation}

Generate a structured animation sequence with:
1. Title introduction
2. Key concept visualization
3. Formula or diagram (if applicable)
4. Example demonstration
5. Summary conclusion
"""
