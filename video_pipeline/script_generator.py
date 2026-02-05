"""
Script Generator - Converts answer text into video script scenes
"""
from typing import List


def generate_script(answer_text: str) -> List[str]:
    """
    Convert answer text into a list of video script scenes.
    
    Args:
        answer_text: The answer text from the LLM
        
    Returns:
        List of scene descriptions for video generation
    """
    # Split text into meaningful chunks (paragraphs)
    # This is a basic heuristic since we don't have the LLM here immediately available
    # unless passed in.
    
    # 1. Clean the text
    text = answer_text.strip()
    
    # 2. Split into paragraphs
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    if not paragraphs:
        paragraphs = [text]
        
    # 3. Create scenes from paragraphs
    # If a paragraph is too long, we might just take the first few sentences
    scenes = []
    
    # Add title scene using the first sentence or a summary check
    if len(paragraphs) > 0:
        first_para = paragraphs[0]
        # customized behavior: if it looks like a title, use it
        scenes.append(first_para)
        
        # Add subsequent paragraphs as scenes, limit to 5 scenes max
        for p in paragraphs[1:5]:
            if len(p) > 20: # smooth out noise
                scenes.append(p)
    
    # Ensure at least one scene
    if not scenes:
        scenes = [answer_text]
        
    return scenes


def generate_detailed_script(answer_text: str) -> List[str]:
    """
    Generate a more detailed script by analyzing the answer.
    This is a placeholder for future LLM-based script generation.
    
    Args:
        answer_text: The answer text from the LLM
        
    Returns:
        List of detailed scene descriptions
    """
    # Future implementation:
    # - Use LLM to analyze the answer
    # - Extract key concepts
    # - Generate scene-by-scene descriptions
    # - Include visual elements, transitions, etc.
    
    return generate_script(answer_text)
