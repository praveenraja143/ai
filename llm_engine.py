"""
LLM Engine - Handles communication with Ollama
Provides educational responses using local LLM
"""
import requests
import json
from typing import Dict, List, Optional
from config import LLM_CONFIG, OLLAMA_CONFIG, SYSTEM_PROMPT


class LLMEngine:
    """Engine for generating educational content using local LLM"""
    
    def __init__(self):
        self.model = LLM_CONFIG["model"]
        self.temperature = LLM_CONFIG["temperature"]
        self.max_tokens = LLM_CONFIG["max_tokens"]
        self.base_url = OLLAMA_CONFIG["base_url"]
        self.timeout = OLLAMA_CONFIG["timeout"]
    
    def generate_response(
        self,
        question: str,
        context: Optional[str] = None
    ) -> Dict:
        """
        Generate an educational response to a question
        
        Args:
            question: The educational question
            context: Optional additional context
            
        Returns:
            Dictionary with answer, topic, and key_concepts
        """
        try:
            # Build the prompt
            prompt = self._build_educational_prompt(question, context)
            
            # Call Ollama API
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens
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
            
            # Parse response
            data = response.json()
            answer = data.get("response", "").strip()
            
            # Extract topic from question
            topic = self._extract_topic(question)
            
            # Extract key concepts from answer
            key_concepts = self._extract_key_concepts(answer)
            
            return {
                "error": False,
                "answer": answer,
                "topic": topic,
                "key_concepts": key_concepts
            }
            
        except requests.exceptions.Timeout:
            return {
                "error": True,
                "answer": "Error: Request timed out. The model may be too slow or not responding.",
                "topic": "Error",
                "key_concepts": []
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
        # Simple extraction - take first few important words
        words = question.lower().split()
        
        # Filter out common question words
        stopwords = {"what", "is", "the", "explain", "how", "why", "tell", "me", "about"}
        important_words = [w for w in words if w not in stopwords]
        
        # Take first 3 important words
        topic_words = important_words[:3]
        topic = " ".join(topic_words).title()
        
        return topic if topic else "General"
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts/formulas from the response"""
        concepts = []
        
        # Look for formulas (simple pattern matching)
        import re
        
        # Pattern 1: Equations with =
        equations = re.findall(r'([A-Za-z0-9\s\+\-\*/\^=\(\)]{5,50}=[^.]{1,50})', text)
        concepts.extend([eq.strip() for eq in equations[:3]])
        
        # Pattern 2: Mathematical expressions in parentheses or brackets
        expressions = re.findall(r'[\(\[]([A-Za-z0-9\s\+\-\*/\^=]{5,40})[\)\]]', text)
        concepts.extend([exp.strip() for exp in expressions[:2]])
        
        return concepts[:5]  # Return max 5 concepts
    
    def list_available_models(self) -> List[str]:
        """List all available models in Ollama"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                return [model["name"] for model in models]
            else:
                return []
                
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """
        Pull/download a model from Ollama
        
        Args:
            model_name: Name of the model to download
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Downloading model: {model_name}")
            print("This may take several minutes...")
            
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=600  # 10 minutes for download
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error pulling model: {e}")
            return False
    
    def check_health(self) -> Dict:
        """Check if Ollama is running and model is available"""
        status = {
            "ollama_running": False,
            "model_available": False,
            "available_models": []
        }
        
        try:
            # Check if Ollama is running
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            
            if response.status_code == 200:
                status["ollama_running"] = True
                
                # Check available models
                data = response.json()
                models = data.get("models", [])
                model_names = [m["name"] for m in models]
                status["available_models"] = model_names
                
                # Check if our model is available
                status["model_available"] = any(
                    self.model in name for name in model_names
                )
            
        except Exception as e:
            print(f"Health check error: {e}")
        
        return status


def check_system_ready() -> Dict:
    """
    Check if the system is ready to use
    
    Returns:
        Dictionary with system status
    """
    engine = LLMEngine()
    health = engine.check_health()
    
    return {
        "system_ready": health["ollama_running"] and health["model_available"],
        "ollama_running": health["ollama_running"],
        "model_available": health["model_available"],
        "available_models": health["available_models"]
    }


# Quick test function
def test_llm():
    """Test the LLM engine"""
    print("Testing LLM Engine...")
    
    engine = LLMEngine()
    
    # Health check
    print("\n1. Health Check:")
    health = engine.check_health()
    print(f"   Ollama running: {health['ollama_running']}")
    print(f"   Model available: {health['model_available']}")
    print(f"   Available models: {health['available_models']}")
    
    if not health['ollama_running']:
        print("\n❌ Ollama is not running!")
        print("   Start it with: ollama serve")
        return
    
    if not health['model_available']:
        print(f"\n❌ Model '{engine.model}' not found!")
        print(f"   Download it with: ollama pull mistral")
        return
    
    # Test generation
    print("\n2. Testing generation:")
    print("   Question: What is 2+2?")
    
    response = engine.generate_response("What is 2+2?")
    
    if response["error"]:
        print(f"   ❌ Error: {response['answer']}")
    else:
        print(f"   ✅ Answer: {response['answer'][:100]}...")
        print(f"   Topic: {response['topic']}")
    
    print("\n✅ LLM Engine test complete!")


if __name__ == "__main__":
    test_llm()
