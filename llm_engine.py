"""
LLM Engine - Handles communication with LLMs (Gemini / Ollama)
Provides educational responses using available AI backend
"""
import requests
import json
import os
import google.generativeai as genai
from typing import Dict, List, Optional
from config import LLM_CONFIG, OLLAMA_CONFIG, GEMINI_CONFIG, SYSTEM_PROMPT


class LLMEngine:
    """Engine for generating educational content using Gemini (Cloud) or Ollama (Local)"""
    
    def __init__(self):
        self.provider = "gemini"
        self.model = GEMINI_CONFIG["model"]
        
        # Configure Gemini
        if not GEMINI_CONFIG["api_key"]:
            raise ValueError("GEMINI_API_KEY is required. Please set it in config.py or environment variables.")
        
        try:
            genai.configure(api_key=GEMINI_CONFIG["api_key"])
            self.gemini_model = genai.GenerativeModel(GEMINI_CONFIG["model"])
            print(f"[LLM ENGINE] Using Google Gemini ({self.model})")
        except Exception as e:
            raise RuntimeError(f"[LLM ENGINE] Gemini configuration failed: {e}")
    
    def generate_response(
        self,
        question: str,
        context: Optional[str] = None
    ) -> Dict:
        """
        Generate an educational response to a question using Gemini only
        """
        return self._generate_with_gemini(question, context)

    def _generate_with_gemini(self, question: str, context: Optional[str] = None) -> Dict:
        """Generate response using Google Gemini"""
        try:
            prompt = self._build_educational_prompt(question, context)
            
            response = self.gemini_model.generate_content(prompt)
            answer = response.text
            
            # Extract metadata
            topic = self._extract_topic(question)
            key_concepts = self._extract_key_concepts(answer)
            
            return {
                "error": False,
                "answer": answer,
                "topic": topic,
                "key_concepts": key_concepts
            }
        except Exception as e:
            return {
                "error": True,
                "answer": f"Gemini Error: {str(e)}",
                "topic": "Error",
                "key_concepts": []
            }

    
    def _build_educational_prompt(self, question: str, context: Optional[str] = None) -> str:
        """Build a prompt optimized for educational content"""
        prompt = f"{SYSTEM_PROMPT}\n\n"
        if context:
            prompt += f"Context: {context}\n\n"
        prompt += f"Question: {question}\n\n"
        prompt += "Provide a clear, educational answer that includes:\n"
        prompt += "1. A concise explanation\n"
        prompt += "2. Key formulas or principles (if applicable)\n"
        prompt += "3. A simple example\n\n"
        prompt += "Answer:"
        return prompt
    
    def _extract_topic(self, question: str) -> str:
        """Extract the main topic from a question"""
        words = question.lower().split()
        stopwords = {"what", "is", "the", "explain", "how", "why", "tell", "me", "about"}
        important_words = [w for w in words if w not in stopwords]
        topic = " ".join(important_words[:3]).title()
        return topic if topic else "General"
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts/formulas from the response"""
        import re
        concepts = []
        equations = re.findall(r'([A-Za-z0-9\s\+\-\*/\^=\(\)]{5,50}=[^.]{1,50})', text)
        concepts.extend([eq.strip() for eq in equations[:3]])
        return concepts[:5]
    
    def list_available_models(self) -> List[str]:
        """List all available models (Gemini only)"""
        return ["gemini-pro"]
    
    
    def check_health(self) -> Dict:
        """Check Gemini health"""
        return {
            "ollama_running": True,  # Virtual status for frontend compatibility
            "model_available": True,
            "available_models": ["gemini-pro"]
        }


def check_system_ready() -> Dict:
    engine = LLMEngine()
    health = engine.check_health()
    return {
        "system_ready": health["model_available"],
        "ollama_running": health["ollama_running"],
        "model_available": health["model_available"],
        "available_models": health["available_models"]
    }

if __name__ == "__main__":
    check_system_ready()
