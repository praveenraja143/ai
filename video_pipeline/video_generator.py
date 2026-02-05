"""
Video Generator - Generates videos using AI images
Hybrid approach: AI-generated images + OpenCV animation
"""
import cv2
import numpy as np
import time
from typing import List
from pathlib import Path
from config import VIDEOS_DIR

# Import AI modules
try:
    from .manim_generator import ManimCodeGenerator
    MANIM_AVAILABLE = True 
except ImportError as e:
    MANIM_AVAILABLE = False
    print(f"[VIDEO PIPELINE] Manim module not available: {e}")


class HybridVideoGenerator:
    """Generates videos using Manim (Primary) or OpenCV text (Fallback)"""
    
    def __init__(self):
        # Initialize text generator (Fallback)
        try:
            from .opencv_text_generator import EnhancedVideoGenerator
            self.text_gen = EnhancedVideoGenerator(Path(VIDEOS_DIR))
        except:
            self.text_gen = None

        self.use_manim = MANIM_AVAILABLE
        if self.use_manim:
            try:
                self.manim_gen = ManimCodeGenerator()
                print("[VIDEO PIPELINE] Manim Generator initialized")
            except Exception as e:
                print(f"[VIDEO PIPELINE] Failed to initialize Manim: {e}")
                self.use_manim = False
        
    def create_video_from_answer(self, answer_text: str, video_id: str, script_scenes: List[str] = None) -> str:
        """
        Create video using Manim
        """
        topic = "Explanation"
        if script_scenes:
            # Join script for context (Manim needs the full flow)
            explanation = "\n".join(script_scenes)
        else:
            explanation = answer_text
            
        if self.use_manim:
            print(f"[VIDEO PIPELINE] Attempting Manim render for {video_id}...")
            video_path = self.manim_gen.generate_video(topic, explanation, video_id)
            
            if video_path:
                print(f"[VIDEO PIPELINE] ✅ Manim video created: {video_path}")
                return video_path
            
        # Fallback
        print("[VIDEO PIPELINE] Manim failed or unavailable. Using standard text video.")
        if self.text_gen:
            return self.text_gen.generate_video(topic, explanation, video_id=video_id)
        return None


# Main function to replace the current implementation
def generate_video(script_scenes: List[str], video_id: str, videos_dir: str = "videos") -> str:
    """
    Generate video from script scenes using hybrid AI approach
    
    Args:
        script_scenes: List of scene descriptions
        video_id: Unique identifier for the video
        videos_dir: Directory to save videos
        
    Returns:
        Path to the generated video file
    """
    print(f"\n[VIDEO PIPELINE] Starting hybrid AI video generation for task {video_id}")
    
    # Get answer text from first scene
    answer_text = script_scenes[0] if script_scenes else "Educational content"
    
    # Create generator and generate video
    generator = HybridVideoGenerator()
    video_path = generator.create_video_from_answer(answer_text, video_id, script_scenes=script_scenes)
    
    if video_path:
        print(f"[VIDEO PIPELINE] Video generation completed successfully")
    else:
        print(f"[VIDEO PIPELINE] Video generation failed")
    
    return f"{videos_dir}/{video_id}.mp4"


def generate_video_with_progress(
    script_scenes: List[str],
    video_id: str,
    videos_dir: str = "videos",
    progress_callback=None
) -> str:
    """
    Generate video with progress tracking
    
    Args:
        script_scenes: List of scene descriptions
        video_id: Unique identifier for the video
        videos_dir: Directory to save videos
        progress_callback: Optional callback function for progress updates
        
    Returns:
        Path to the generated video file
    """
    # For now, just call the main function
    # Future: Add progress tracking during image generation
    return generate_video(script_scenes, video_id, videos_dir)
