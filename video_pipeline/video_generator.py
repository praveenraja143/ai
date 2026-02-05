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
        self.use_ai = AI_AVAILABLE
        if self.use_ai:
            try:
                self.image_gen = AIImageGenerator()
                self.animator = ImageToVideoAnimator()
                print("[VIDEO PIPELINE] Hybrid AI video generator initialized")
            except Exception as e:
                print(f"[VIDEO PIPELINE] Failed to initialize AI: {e}")
                self.use_ai = False
        
        # Fallback to text-based generator
        if not self.use_ai:
            # Import the legacy OpenCV text generator
            import sys
            import cv2
            import numpy as np
            from pathlib import Path
            from config import VIDEOS_DIR
            
            # Create a simple text-based video generator inline
            class SimpleTextGenerator:
                def __init__(self):
                    self.width = 1280
                    self.height = 720
                    self.fps = 30
                    self.bg_color = (15, 15, 35)
                    self.text_color = (255, 255, 255)
                    self.accent_color = (100, 200, 255)
                
                def create_video_from_answer(self, answer_text: str, video_id: str, duration: int = 10) -> str:
                    try:
                        output_path = Path(VIDEOS_DIR) / f"{video_id}.mp4"
                        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                        out = cv2.VideoWriter(str(output_path), fourcc, self.fps, (self.width, self.height))
                        
                        total_frames = duration * self.fps
                        title = answer_text[:50] if len(answer_text) > 50 else answer_text
                        
                        for frame_num in range(total_frames):
                            frame = np.full((self.height, self.width, 3), self.bg_color, dtype=np.uint8)
                            progress = frame_num / total_frames
                            
                            # Simple title display
                            if progress < 0.3:
                                alpha = progress / 0.3
                                color = tuple(int(c * alpha) for c in self.text_color)
                                cv2.putText(frame, title, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
                            else:
                                cv2.putText(frame, title, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, self.text_color, 3)
                                
                                # Show text content
                                y_pos = 200
                                for line in answer_text[:500].split('\n')[:8]:
                                    if line.strip():
                                        cv2.putText(frame, line[:80], (50, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.text_color, 1)
                                        y_pos += 40
                            
                            out.write(frame)
                        
                        out.release()
                        print(f"✅ Text video created: {output_path}")
                        return str(output_path)
                    except Exception as e:
                        print(f"❌ Error creating text video: {e}")
                        return None
            
            self.text_gen = SimpleTextGenerator()
    
    def create_video_from_answer(self, answer_text: str, video_id: str) -> str:
        """
        Create video from answer text using AI images
        
        Args:
            answer_text: The answer text to visualize
            video_id: Unique identifier for the video
            
        Returns:
            Path to the generated video file
        """
        if not self.use_ai:
            print("[VIDEO PIPELINE] Using fallback text-based generator")
            return self.text_gen.create_video_from_answer(answer_text, video_id, duration=10)
        
        try:
            print(f"\n[VIDEO PIPELINE] Generating AI video for task {video_id}")
            
            # Step 1: Generate AI images for scenes
            print("[VIDEO PIPELINE] Step 1: Generating AI images...")
            image_paths = self.image_gen.generate_scene_images(answer_text, video_id, num_scenes=3)
            
            if not image_paths or len(image_paths) == 0:
                print("[VIDEO PIPELINE] No images generated, falling back to text video")
                return self.text_gen.create_video_from_answer(answer_text, video_id, duration=10)
            
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
                return self.text_gen.create_video_from_answer(answer_text, video_id, duration=10)
                
        except Exception as e:
            print(f"[VIDEO PIPELINE] Error in AI video generation: {e}")
            import traceback
            traceback.print_exc()
            print("[VIDEO PIPELINE] Falling back to text-based generator")
            return self.text_gen.create_video_from_answer(answer_text, video_id, duration=10)


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
