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
        self.provider = "ollama"
        self.model = LLM_CONFIG["model"]
        
        # Check for Gemini API Key
        if GEMINI_CONFIG["api_key"]:
            try:
                genai.configure(api_key=GEMINI_CONFIG["api_key"])
                self.gemini_model = genai.GenerativeModel(GEMINI_CONFIG["model"])
                self.provider = "gemini"
                self.model = GEMINI_CONFIG["model"]
                print(f"[LLM ENGINE] Using Google Gemini ({self.model})")
            except Exception as e:
                print(f"[LLM ENGINE] Gemini configuration failed: {e}")
                
        if self.provider == "ollama":
            self.base_url = OLLAMA_CONFIG["base_url"]
            self.timeout = OLLAMA_CONFIG["timeout"]
            print(f"[LLM ENGINE] Using Local Ollama ({self.model})")
    
    def generate_response(
        self,
        question: str,
        context: Optional[str] = None
    ) -> Dict:
        """
        Generate an educational response to a question
        """
        if self.provider == "gemini":
            return self._generate_with_gemini(question, context)
        else:
            return self._generate_with_ollama(question, context)

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

    def _generate_with_ollama(self, question: str, context: Optional[str] = None) -> Dict:
        """Generate response using Ollama"""
        try:
            prompt = self._build_educational_prompt(question, context)
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": LLM_CONFIG["temperature"],
                        "num_predict": LLM_CONFIG["max_tokens"]
                    }
                },
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                return {
                    "error": True,
                    "answer": f"Error: Ollama returned status {response.status_code}",
                    "topic": "Error",
                    "key_concepts": []
                }
            
            data = response.json()
            answer = data.get("response", "").strip()
            
            topic = self._extract_topic(question)
            key_concepts = self._extract_key_concepts(answer)
            
            return {
                "error": False,
                "answer": answer,
                "topic": topic,
                "key_concepts": key_concepts
            }
            
        except requests.exceptions.ConnectionError:
            return {
                "error": True,
                "answer": "Error: Cannot connect to Ollama. Make sure 'ollama serve' is running.",
                "topic": "Error",
                "key_concepts": []
            }
        except Exception as e:
            return {
                "error": True,
                "answer": f"Error: {str(e)}",
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
        """List all available models"""
        if self.provider == "gemini":
            return ["gemini-pro"]
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return [m["name"] for m in response.json().get("models", [])]
        except:
            pass
        return []
    
    def pull_model(self, model_name: str) -> bool:
        """Pull a model (Ollama only)"""
        if self.provider != "ollama":
            return True
        try:
            requests.post(f"{self.base_url}/api/pull", json={"name": model_name}, timeout=600)
            return True
        except:
            return False

    def check_health(self) -> Dict:
        """Check system health"""
        status = {
            "ollama_running": False,
            "model_available": False,
            "available_models": []
        }
        
        if self.provider == "gemini":
            status["ollama_running"] = True # Virtual status for frontend
            status["model_available"] = True
            status["available_models"] = ["gemini-pro"]
            return status
            
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                status["ollama_running"] = True
                models = [m["name"] for m in response.json().get("models", [])]
                status["available_models"] = models
                status["model_available"] = any(self.model in name for name in models)
        except:
            pass
        return status


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
