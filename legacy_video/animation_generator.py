"""
Animation Generator - Creates educational videos
Uses lightweight OpenCV-based generator to avoid memory issues
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from config import VIDEOS_DIR
from simple_video_generator import EnhancedVideoGenerator


class AnimationGenerator:
    """Main class for generating educational animations"""
    
    def __init__(self):
        self.generator = EnhancedVideoGenerator(VIDEOS_DIR)
    
    def generate_video(
        self,
        topic: str,
        explanation: str,
        formulas: List[str] = None,
        video_id: str = None
    ) -> Optional[str]:
        """
        Generate an educational animation video
        
        Args:
            topic: The topic/title of the video
            explanation: Text explanation
            formulas: List of mathematical formulas
            video_id: Unique identifier for the video
            
        Returns:
            Path to the generated video file, or None if failed
        """
        try:
            print(f"📹 Generating video for: {topic}")
            result = self.generator.generate_video(
                topic=topic,
                explanation=explanation,
                formulas=formulas or [],
                video_id=video_id,
                duration=10  # 10 second videos
            )
            if result:
                print(f"✅ Video generated successfully: {result}")
            return result
        except Exception as e:
            print(f"❌ Error generating video: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def extract_formulas(self, text: str) -> List[str]:
        """Extract mathematical formulas from text"""
        formulas = []
        
        # Pattern 1: Equations (e.g., "a^2 + b^2 = c^2")
        equation_pattern = r'([a-zA-Z0-9\s\+\-\*/\^=\(\)]+=[^.]+)'
        equations = re.findall(equation_pattern, text)
        formulas.extend([eq.strip() for eq in equations])
        
        # Pattern 2: Common mathematical expressions
        # Look for patterns like "P(A|B) = ..."
        prob_pattern = r'P\([^)]+\)\s*=\s*[^.]+'
        prob_formulas = re.findall(prob_pattern, text)
        formulas.extend([f.strip() for f in prob_formulas])
        
        return formulas[:3]  # Limit to 3 formulas


# Utility function for quick video generation
def create_educational_video(
    topic: str,
    explanation: str,
    formulas: List[str] = None,
    video_id: str = None
) -> Optional[str]:
    """
    Quick function to create an educational video
    
    Returns:
        Path to generated video or None
    """
    generator = AnimationGenerator()
    return generator.generate_video(topic, explanation, formulas, video_id)


if __name__ == "__main__":
    # Test the animation generator
    print("Testing Animation Generator...")
    
    test_topic = "Pythagorean Theorem"
    test_explanation = "The Pythagorean theorem states that in a right triangle, the square of the hypotenuse equals the sum of squares of the other two sides."
    test_formulas = ["a^2 + b^2 = c^2"]
    
    print(f"Generating video for: {test_topic}")
    video_path = create_educational_video(
        topic=test_topic,
        explanation=test_explanation,
        formulas=test_formulas,
        video_id="test"
    )
    
    if video_path:
        print(f"✅ Video generated: {video_path}")
    else:
        print("❌ Failed to generate video")
