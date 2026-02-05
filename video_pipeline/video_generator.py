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
    from .ai_image_generator import AIImageGenerator
    from .image_to_video import ImageToVideoAnimator
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("[VIDEO PIPELINE] AI modules not available, using fallback")


class HybridVideoGenerator:
    """Generates videos using AI images and OpenCV animation"""
    
    def __init__(self):
    def __init__(self):
        # Initialize text generator (Always available as fallback)
        try:
            from .opencv_text_generator import EnhancedVideoGenerator
            self.text_gen = EnhancedVideoGenerator(Path(VIDEOS_DIR))
            print("[VIDEO PIPELINE] Enhanced video generator initialized")
        except Exception as e:
            print(f"[VIDEO PIPELINE] Failed to initialize EnhancedVideoGenerator: {e}")
            self.text_gen = None

        self.use_ai = AI_AVAILABLE
        if self.use_ai:
            try:
                self.image_gen = AIImageGenerator()
                self.animator = ImageToVideoAnimator()
                print("[VIDEO PIPELINE] Hybrid AI video generator initialized")
            except Exception as e:
                print(f"[VIDEO PIPELINE] Failed to initialize AI: {e}")
                self.use_ai = False
        
        if not self.use_ai:
             print("[VIDEO PIPELINE] AI modules unavailable. Using pure EnhancedVideoGenerator.")

    def create_video_from_answer(self, answer_text: str, video_id: str) -> str:
        """
        Create video from answer text using AI images or fallback
        """
        if not self.use_ai or not hasattr(self, 'image_gen'):
            print("[VIDEO PIPELINE] Using Enhanced Video Generator")
            if self.text_gen:
                # Extract a topic from the first line or use default
                lines = answer_text.split('\n')
                topic = lines[0] if lines else "Explanation"
                explanation = "\n".join(lines[1:]) if len(lines) > 1 else answer_text
                
                return self.text_gen.generate_video(topic, explanation, video_id=video_id, duration=15)
            else:
                return None
        
        try:
            print(f"\n[VIDEO PIPELINE] Generating AI video for task {video_id}")
            
            # Step 1: Generate AI images for scenes
            print("[VIDEO PIPELINE] Step 1: Generating AI images...")
            image_paths = self.image_gen.generate_scene_images(answer_text, video_id, num_scenes=3)
            
            if not image_paths or len(image_paths) == 0:
                print("[VIDEO PIPELINE] No images generated, falling back to enhanced video")
                if self.text_gen:
                    return self.text_gen.generate_video("Explanation", answer_text, video_id=video_id)
                return None
            
            # Step 2: Create video from images
            print("[VIDEO PIPELINE] Step 2: Creating video from images...")
            output_path = Path(VIDEOS_DIR) / f"{video_id}.mp4"
            video_path = self.animator.create_video_from_images(
                image_paths,
                str(output_path),
                duration_per_image=3,
                transition_duration=0.5
            )
            
            if video_path:
                print(f"[VIDEO PIPELINE] ✅ AI video created: {video_path}")
                return str(output_path)
            else:
                print("[VIDEO PIPELINE] Video creation failed, using fallback")
                if self.text_gen:
                    return self.text_gen.generate_video("Explanation", answer_text, video_id=video_id)
                return None
                
        except Exception as e:
            print(f"[VIDEO PIPELINE] Error in AI video generation: {e}")
            print("[VIDEO PIPELINE] Falling back to enhanced generator")
            if self.text_gen:
                return self.text_gen.generate_video("Error Fallback", answer_text, video_id=video_id)
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
    video_path = generator.create_video_from_answer(answer_text, video_id)
    
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
