"""
Script Generator - Converts answer text into an animated story script
"""
from typing import List
import google.generativeai as genai
from config import GEMINI_CONFIG

def generate_script(answer_text: str) -> List[str]:
    """
    Convert answer text into a 3-part animated story script using Gemini.
    """
    try:
        genai.configure(api_key=GEMINI_CONFIG["api_key"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        You are a screenwriter for a 3D animated educational series (Pixar style).
        Convert this educational answer into a short 3-scene story script.
        
        Input Answer: "{answer_text[:1000]}"
        
        Requirements:
        - Output EXACTLY 3 paragraphs.
        - Scene 1: The Hook. Introduce a character or visual metaphor facing a problem related to the concept.
        - Scene 2: The Action. The character uses the concept (the mechanism) to solve it.
        - Scene 3: The Resolution. A happy ending showing the real-world value.
        - Style: Engaging, narrative, visual. Avoid "Scene 1:" labels if possible, just the story text.
        
        Output Format:
        Paragraph 1 (Scene 1 Description)
        Paragraph 2 (Scene 2 Description)
        Paragraph 3 (Scene 3 Description)
        """
        
        response = model.generate_content(prompt)
        scenes = [p.strip() for p in response.text.split('\n\n') if p.strip()]
        
        return scenes[:3] if len(scenes) >= 3 else scenes
        
    except Exception as e:
        print(f"[SCRIPT GEN] Error transforming script: {e}")
        # Fallback to simple splitting
        return [answer_text]

def generate_detailed_script(answer_text: str) -> List[str]:
    """Alias for consistency"""
    return generate_script(answer_text)
