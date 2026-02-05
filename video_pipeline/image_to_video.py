"""
Image to Video Animator - Creates videos from AI-generated images
"""
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import List


class ImageToVideoAnimator:
    """Creates animated videos from images"""
    
    def __init__(self):
        self.width = 1280
        self.height = 720
        self.fps = 30
        
    def _apply_ken_burns_effect(self, img: np.ndarray, frames: int) -> List[np.ndarray]:
        """Apply Ken Burns (Zoom/Pan) effect to an image"""
        h, w = img.shape[:2]
        motion_frames = []
        
        # Randomly choose zoom direction (in or out)
        zoom_factor = 1.15  # Zoom in/out by 15%
        
        # Center crop (full view)
        center_x, center_y = w // 2, h // 2
        
        for i in range(frames):
            progress = i / frames
            scale = 1.0 + (zoom_factor - 1.0) * progress
            
            # Create rotation matrix for scaling from center
            M = cv2.getRotationMatrix2D((center_x, center_y), 0, scale)
            result = cv2.warpAffine(img, M, (w, h))
            motion_frames.append(result)
            
        return motion_frames

    def create_video_from_images(
        self,
        image_paths: List[str],
        output_path: str,
        duration_per_image: int = 4,  # Increased duration for effect
        transition_duration: float = 0.5
    ) -> str:
        """Create video with Ken Burns effect"""
        try:
            print(f"[VIDEO ANIMATOR] Creating animated story from {len(image_paths)} scenes...")
            
            # Create video writer
            try:
                fourcc = cv2.VideoWriter_fourcc(*'avc1')
            except:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                
            out = cv2.VideoWriter(output_path, fourcc, self.fps, (self.width, self.height))
            
            for i, img_path in enumerate(image_paths):
                # Load resizing
                img = self._load_and_resize_image(img_path)
                
                # Generate motion frames
                static_frames_count = int((duration_per_image - transition_duration) * self.fps)
                motion_sequence = self._apply_ken_burns_effect(img, static_frames_count)
                
                for frame in motion_sequence:
                    out.write(frame)
                
                # Transition (Cross-fade)
                if i < len(image_paths) - 1:
                    next_img = self._load_and_resize_image(image_paths[i + 1])
                    next_start = self._apply_ken_burns_effect(next_img, 1)[0] # Start state of next
                    
                    last_frame = motion_sequence[-1]
                    trans_frames = int(transition_duration * self.fps)
                    
                    for f in range(trans_frames):
                        alpha = f / trans_frames
                        blended = cv2.addWeighted(last_frame, 1 - alpha, next_start, alpha, 0)
                        out.write(blended)
                        
            out.release()
            print(f"[VIDEO ANIMATOR] Animated story created: {output_path}")
            return output_path
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _load_and_resize_image(self, image_path: str) -> np.ndarray:
        """Load image and resize to video dimensions"""
        # Load image
        img = cv2.imread(image_path)
        
        if img is None:
            # Create a placeholder if image failed to load
            img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            cv2.putText(
                img, "Image not found", 
                (self.width // 2 - 100, self.height // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
            )
            return img
        
        # Resize to fit video dimensions while maintaining aspect ratio
        h, w = img.shape[:2]
        aspect = w / h
        target_aspect = self.width / self.height
        
        if aspect > target_aspect:
            # Image is wider
            new_w = self.width
            new_h = int(self.width / aspect)
        else:
            # Image is taller
            new_h = self.height
            new_w = int(self.height * aspect)
        
        resized = cv2.resize(img, (new_w, new_h))
        
        # Create canvas and center image
        canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        y_offset = (self.height - new_h) // 2
        x_offset = (self.width - new_w) // 2
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        
        return canvas
    
    def add_text_overlay(
        self,
        frame: np.ndarray,
        text: str,
        position: tuple = None,
        font_scale: float = 1.0
    ) -> np.ndarray:
        """Add text overlay to a frame"""
        if position is None:
            position = (50, self.height - 50)
        
        # Add semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (position[0] - 10, position[1] - 40),
            (position[0] + len(text) * 20, position[1] + 10),
            (0, 0, 0),
            -1
        )
        frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
        
        # Add text
        cv2.putText(
            frame,
            text,
            position,
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (255, 255, 255),
            2
        )
        
        return frame
