"""
Enhanced Video Generator - Creates step-by-step educational animations
Visualizes concepts with drawings, shapes, and animations
"""
import cv2
import numpy as np
from pathlib import Path
from typing import List, Optional, Tuple
import re
import math


class EnhancedVideoGenerator:
    """Generates educational videos with visual explanations"""
    
    def __init__(self, videos_dir: Path):
        self.videos_dir = videos_dir
        self.width = 1280
        self.height = 720
        self.fps = 30
        self.bg_color = (15, 15, 35)  # Dark blue background
        self.text_color = (255, 255, 255)  # White
        self.accent_color = (100, 200, 255)  # Light blue
        self.success_color = (100, 255, 100)  # Green
        self.warning_color = (255, 200, 100)  # Orange
        
    def generate_video(
        self,
        topic: str,
        explanation: str,
        formulas: List[str] = None,
        video_id: str = None,
        duration: int = 15
    ) -> Optional[str]:
        """Generate an educational animation video"""
        try:
            if video_id is None:
                import uuid
                video_id = str(uuid.uuid4())[:8]
            
            filename = f"{video_id}.mp4"
            output_path = self.videos_dir / filename
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(
                str(output_path),
                fourcc,
                self.fps,
                (self.width, self.height)
            )
            
            # Detect the type of content
            animation_type = self._detect_animation_type(topic, explanation, formulas)
            
            total_frames = duration * self.fps
            
            # Generate frames based on type
            for frame_num in range(total_frames):
                progress = frame_num / total_frames
                
                if animation_type == "math_addition":
                    frame = self._create_math_addition_frame(
                        frame_num, total_frames, topic, explanation, formulas
                    )
                elif animation_type == "math_formula":
                    frame = self._create_formula_explanation_frame(
                        frame_num, total_frames, topic, explanation, formulas
                    )
                elif animation_type == "theorem":
                    frame = self._create_theorem_frame(
                        frame_num, total_frames, topic, explanation, formulas
                    )
                else:
                    # Default: step-by-step explanation
                    frame = self._create_step_by_step_frame(
                        frame_num, total_frames, topic, explanation, formulas
                    )
                
                out.write(frame)
            
            out.release()
            print(f"✅ Enhanced video generated: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ Error generating video: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _detect_animation_type(self, topic: str, explanation: str, formulas: List[str]) -> str:
        """Detect what type of animation to create"""
        topic_lower = topic.lower()
        explanation_lower = explanation.lower()
        
        # Check for simple addition/subtraction
        if re.search(r'\d+\s*[\+\-]\s*\d+', topic_lower) or re.search(r'\d+\s*[\+\-]\s*\d+', explanation_lower):
            return "math_addition"
        
        # Check for theorems
        if "theorem" in topic_lower or "law" in topic_lower:
            return "theorem"
        
        # Check for formulas
        if formulas and len(formulas) > 0:
            return "math_formula"
        
        return "step_by_step"
    
    def _create_math_addition_frame(
        self, frame_num: int, total_frames: int,
        topic: str, explanation: str, formulas: List[str]
    ) -> np.ndarray:
        """Create frame for math addition/subtraction with visual objects"""
        frame = np.full((self.height, self.width, 3), self.bg_color, dtype=np.uint8)
        progress = frame_num / total_frames
        
        # Extract numbers from topic or explanation
        numbers = re.findall(r'\d+', topic + " " + explanation)
        
        if len(numbers) >= 2:
            num1 = int(numbers[0])
            num2 = int(numbers[1])
            result = num1 + num2  # Assuming addition for now
            
            # Stage 1: Show title (0-15%)
            if progress < 0.15:
                alpha = progress / 0.15
                self._draw_title(frame, topic, alpha)
            
            # Stage 2: Show first group of objects (15-35%)
            elif progress < 0.35:
                self._draw_title(frame, topic, 1.0)
                section_progress = (progress - 0.15) / 0.2
                self._draw_objects_group(frame, num1, 200, 300, section_progress, "First Group")
                self._draw_large_number(frame, str(num1), 200, 500, section_progress)
            
            # Stage 3: Show plus sign (35-45%)
            elif progress < 0.45:
                self._draw_title(frame, topic, 1.0)
                self._draw_objects_group(frame, num1, 200, 300, 1.0, "First Group")
                self._draw_large_number(frame, str(num1), 200, 500, 1.0)
                section_progress = (progress - 0.35) / 0.1
                self._draw_operator(frame, "+", self.width // 2, 400, section_progress)
            
            # Stage 4: Show second group (45-65%)
            elif progress < 0.65:
                self._draw_title(frame, topic, 1.0)
                self._draw_objects_group(frame, num1, 200, 300, 1.0, "First Group")
                self._draw_large_number(frame, str(num1), 200, 500, 1.0)
                self._draw_operator(frame, "+", self.width // 2, 400, 1.0)
                section_progress = (progress - 0.45) / 0.2
                self._draw_objects_group(frame, num2, 1080, 300, section_progress, "Second Group")
                self._draw_large_number(frame, str(num2), 1080, 500, section_progress)
            
            # Stage 5: Combine and show result (65-85%)
            elif progress < 0.85:
                self._draw_title(frame, topic, 1.0)
                section_progress = (progress - 0.65) / 0.2
                
                # Move objects together
                offset = int(section_progress * 300)
                self._draw_objects_group(frame, num1, 200 + offset, 300, 1.0, "")
                self._draw_objects_group(frame, num2, 1080 - offset, 300, 1.0, "")
                
                # Show equals and result
                if section_progress > 0.5:
                    result_alpha = (section_progress - 0.5) / 0.5
                    self._draw_operator(frame, "=", self.width // 2, 550, result_alpha)
                    self._draw_large_number(frame, str(result), self.width // 2, 600, result_alpha, color=self.success_color)
            
            # Stage 6: Final answer (85-100%)
            else:
                section_progress = (progress - 0.85) / 0.15
                self._draw_conclusion(frame, f"{num1} + {num2} = {result}", section_progress)
        else:
            # Fallback to step-by-step
            return self._create_step_by_step_frame(frame_num, total_frames, topic, explanation, formulas)
        
        return frame
    
    def _draw_objects_group(self, frame: np.ndarray, count: int, x: int, y: int, alpha: float, label: str):
        """Draw a group of circular objects (balls)"""
        # Limit to max 10 objects for visibility
        visible_count = min(count, 10)
        items_to_show = int(visible_count * alpha)
        
        if items_to_show == 0:
            return
        
        # Calculate grid layout
        cols = min(5, visible_count)
        rows = (visible_count + cols - 1) // cols
        
        spacing = 60
        start_x = x - (cols * spacing) // 2
        start_y = y - (rows * spacing) // 2
        
        # Draw label
        if label and alpha > 0.5:
            cv2.putText(frame, label, (start_x, start_y - 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.text_color, 2)
        
        # Draw objects
        for i in range(items_to_show):
            row = i // cols
            col = i % cols
            
            obj_x = start_x + col * spacing
            obj_y = start_y + row * spacing
            
            # Draw circle (ball)
            radius = 20
            
            # Shadow
            cv2.circle(frame, (obj_x + 3, obj_y + 3), radius, (0, 0, 0), -1)
            
            # Main circle with gradient effect
            cv2.circle(frame, (obj_x, obj_y), radius, self.accent_color, -1)
            
            # Highlight
            cv2.circle(frame, (obj_x - 5, obj_y - 5), 6, (200, 230, 255), -1)
        
        # Show count if more than 10
        if count > 10:
            count_text = f"x{count}"
            cv2.putText(frame, count_text, (start_x, start_y + rows * spacing + 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, self.warning_color, 2)
    
    def _draw_large_number(self, frame: np.ndarray, number: str, x: int, y: int, alpha: float, color=None):
        """Draw a large number"""
        if color is None:
            color = self.accent_color
        
        actual_color = tuple(int(c * alpha) for c in color)
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2.0
        thickness = 5
        
        text_size = cv2.getTextSize(number, font, font_scale, thickness)[0]
        text_x = x - text_size[0] // 2
        
        # Shadow
        cv2.putText(frame, number, (text_x + 3, y + 3), font, font_scale, (0, 0, 0), thickness)
        
        # Main text
        cv2.putText(frame, number, (text_x, y), font, font_scale, actual_color, thickness)
    
    def _draw_operator(self, frame: np.ndarray, operator: str, x: int, y: int, alpha: float):
        """Draw a mathematical operator"""
        color = tuple(int(c * alpha) for c in self.warning_color)
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 3.0
        thickness = 6
        
        text_size = cv2.getTextSize(operator, font, font_scale, thickness)[0]
        text_x = x - text_size[0] // 2
        
        # Shadow
        cv2.putText(frame, operator, (text_x + 4, y + 4), font, font_scale, (0, 0, 0), thickness)
        
        # Main text
        cv2.putText(frame, operator, (text_x, y), font, font_scale, color, thickness)
    
    def _create_formula_explanation_frame(
        self, frame_num: int, total_frames: int,
        topic: str, explanation: str, formulas: List[str]
    ) -> np.ndarray:
        """Create frame explaining a formula step by step"""
        frame = np.full((self.height, self.width, 3), self.bg_color, dtype=np.uint8)
        progress = frame_num / total_frames
        
        # Stage 1: Title (0-15%)
        if progress < 0.15:
            alpha = progress / 0.15
            self._draw_title(frame, topic, alpha)
        
        # Stage 2: Show formula (15-40%)
        elif progress < 0.40:
            self._draw_title(frame, topic, 1.0)
            section_progress = (progress - 0.15) / 0.25
            if formulas:
                self._draw_centered_formula(frame, formulas[0], 200, section_progress)
        
        # Stage 3: Explanation (40-80%)
        elif progress < 0.80:
            self._draw_title(frame, topic, 1.0)
            if formulas:
                self._draw_centered_formula(frame, formulas[0], 200, 1.0)
            section_progress = (progress - 0.40) / 0.40
            self._draw_wrapped_explanation(frame, explanation, 350, section_progress)
        
        # Stage 4: Conclusion (80-100%)
        else:
            section_progress = (progress - 0.80) / 0.20
            formula_text = formulas[0] if formulas else topic
            self._draw_conclusion(frame, formula_text, section_progress)
        
        return frame
    
    def _create_theorem_frame(
        self, frame_num: int, total_frames: int,
        topic: str, explanation: str, formulas: List[str]
    ) -> np.ndarray:
        """Create frame for theorems with diagrams"""
        frame = np.full((self.height, self.width, 3), self.bg_color, dtype=np.uint8)
        progress = frame_num / total_frames
        
        # For Pythagorean theorem, draw a triangle
        if "pythag" in topic.lower():
            return self._create_pythagorean_frame(frame, frame_num, total_frames, topic, explanation, formulas)
        
        # Default theorem visualization
        return self._create_step_by_step_frame(frame_num, total_frames, topic, explanation, formulas)
    
    def _create_pythagorean_frame(
        self, frame: np.ndarray, frame_num: int, total_frames: int,
        topic: str, explanation: str, formulas: List[str]
    ) -> np.ndarray:
        """Create Pythagorean theorem animation"""
        progress = frame_num / total_frames
        
        # Stage 1: Title
        if progress < 0.15:
            alpha = progress / 0.15
            self._draw_title(frame, topic, alpha)
        
        # Stage 2: Draw triangle
        elif progress < 0.50:
            self._draw_title(frame, topic, 1.0)
            section_progress = (progress - 0.15) / 0.35
            self._draw_right_triangle(frame, section_progress)
        
        # Stage 3: Show formula
        elif progress < 0.75:
            self._draw_title(frame, topic, 1.0)
            self._draw_right_triangle(frame, 1.0)
            section_progress = (progress - 0.50) / 0.25
            if formulas:
                self._draw_centered_formula(frame, formulas[0], 550, section_progress)
        
        # Stage 4: Conclusion
        else:
            section_progress = (progress - 0.75) / 0.25
            formula_text = formulas[0] if formulas else "a² + b² = c²"
            self._draw_conclusion(frame, formula_text, section_progress)
        
        return frame
    
    def _draw_right_triangle(self, frame: np.ndarray, alpha: float):
        """Draw a right triangle with labels"""
        # Triangle points
        center_x = self.width // 2
        center_y = 350
        
        size = int(200 * alpha)
        
        pt1 = (center_x - size, center_y + size)  # Bottom left
        pt2 = (center_x + size, center_y + size)  # Bottom right
        pt3 = (center_x + size, center_y - size)  # Top right
        
        # Draw triangle
        if alpha > 0.2:
            pts = np.array([pt1, pt2, pt3], np.int32)
            
            # Fill
            cv2.fillPoly(frame, [pts], (40, 40, 60))
            
            # Outline
            cv2.polylines(frame, [pts], True, self.accent_color, 3)
        
        # Draw right angle indicator
        if alpha > 0.5:
            square_size = 30
            cv2.rectangle(frame, 
                         (pt2[0] - square_size, pt2[1] - square_size),
                         (pt2[0], pt2[1]),
                         self.warning_color, 2)
        
        # Labels
        if alpha > 0.7:
            label_alpha = (alpha - 0.7) / 0.3
            color = tuple(int(c * label_alpha) for c in self.text_color)
            
            cv2.putText(frame, "a", (center_x - size // 2, center_y + size + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
            cv2.putText(frame, "b", (center_x + size + 20, center_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
            cv2.putText(frame, "c", (center_x, center_y - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
    
    def _create_step_by_step_frame(
        self, frame_num: int, total_frames: int,
        topic: str, explanation: str, formulas: List[str]
    ) -> np.ndarray:
        """Create default step-by-step explanation frame"""
        frame = np.full((self.height, self.width, 3), self.bg_color, dtype=np.uint8)
        progress = frame_num / total_frames
        
        # Stage 1: Title
        if progress < 0.2:
            alpha = progress / 0.2
            self._draw_title(frame, topic, alpha)
        
        # Stage 2: Explanation
        elif progress < 0.7:
            self._draw_title(frame, topic, 1.0)
            section_progress = (progress - 0.2) / 0.5
            self._draw_wrapped_explanation(frame, explanation, 200, section_progress)
        
        # Stage 3: Formula (if available)
        elif progress < 0.9:
            self._draw_title(frame, topic, 1.0)
            self._draw_wrapped_explanation(frame, explanation, 200, 1.0)
            if formulas:
                section_progress = (progress - 0.7) / 0.2
                self._draw_centered_formula(frame, formulas[0], 550, section_progress)
        
        # Stage 4: Conclusion
        else:
            section_progress = (progress - 0.9) / 0.1
            self._draw_conclusion(frame, topic, section_progress)
        
        return frame
    
    def _draw_title(self, frame: np.ndarray, title: str, alpha: float):
        """Draw title with fade-in"""
        if len(title) > 50:
            title = title[:47] + "..."
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.5
        thickness = 4
        
        text_size = cv2.getTextSize(title, font, font_scale, thickness)[0]
        x = (self.width - text_size[0]) // 2
        y = 80
        
        color = tuple(int(c * alpha) for c in self.accent_color)
        
        # Shadow
        cv2.putText(frame, title, (x + 3, y + 3), font, font_scale, (0, 0, 0), thickness)
        
        # Main text
        cv2.putText(frame, title, (x, y), font, font_scale, color, thickness)
        
        # Underline
        line_y = y + 15
        line_length = int(text_size[0] * alpha)
        cv2.line(frame, (x, line_y), (x + line_length, line_y), self.accent_color, 3)
    
    def _draw_wrapped_explanation(self, frame: np.ndarray, text: str, start_y: int, alpha: float):
        """Draw explanation text with word wrapping"""
        words = text.split()
        lines = []
        current_line = []
        max_chars = 70
        
        for word in words:
            test_line = " ".join(current_line + [word])
            if len(test_line) <= max_chars:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(" ".join(current_line))
        
        lines = lines[:10]  # Max 10 lines
        
        num_lines_to_show = min(len(lines), int(len(lines) * alpha) + 1)
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.8
        thickness = 2
        line_height = 45
        
        for i, line in enumerate(lines[:num_lines_to_show]):
            y = start_y + (i * line_height)
            x = 50
            
            if i == num_lines_to_show - 1:
                line_alpha = min(1.0, (alpha * len(lines)) % 1.0 + 0.3)
                color = tuple(int(c * line_alpha) for c in self.text_color)
            else:
                color = self.text_color
            
            cv2.putText(frame, line, (x, y), font, font_scale, color, thickness)
    
    def _draw_centered_formula(self, frame: np.ndarray, formula: str, y: int, alpha: float):
        """Draw a formula centered on screen"""
        if len(formula) > 60:
            formula = formula[:57] + "..."
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.2
        thickness = 3
        
        text_size = cv2.getTextSize(formula, font, font_scale, thickness)[0]
        x = (self.width - text_size[0]) // 2
        
        color = tuple(int(c * alpha) for c in self.success_color)
        
        # Box background
        padding = 25
        box_alpha = int(100 * alpha)
        overlay = frame.copy()
        cv2.rectangle(overlay,
                     (x - padding, y - 40),
                     (x + text_size[0] + padding, y + 15),
                     (50, 50, 70), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Box border
        cv2.rectangle(frame,
                     (x - padding, y - 40),
                     (x + text_size[0] + padding, y + 15),
                     self.success_color, 3)
        
        # Formula text
        cv2.putText(frame, formula, (x, y), font, font_scale, color, thickness)
    
    def _draw_conclusion(self, frame: np.ndarray, text: str, alpha: float):
        """Draw conclusion screen"""
        # Background circle animation
        max_radius = int(400 * alpha)
        center = (self.width // 2, self.height // 2)
        
        for i in range(3, 0, -1):
            radius = max_radius - (i * 50)
            if radius > 0:
                cv2.circle(frame, center, radius, (30, 30, 50), 2)
        
        # Main text
        if len(text) > 40:
            text = text[:37] + "..."
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2.0
        thickness = 5
        
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        x = (self.width - text_size[0]) // 2
        y = self.height // 2
        
        color = tuple(int(c * alpha) for c in self.success_color)
        
        # Shadow
        cv2.putText(frame, text, (x + 4, y + 4), font, font_scale, (0, 0, 0), thickness)
        
        # Main
        cv2.putText(frame, text, (x, y), font, font_scale, color, thickness)
        
        # Checkmark
        if alpha > 0.5:
            check_alpha = (alpha - 0.5) / 0.5
            check_color = tuple(int(c * check_alpha) for c in self.success_color)
            check_size = int(60 * check_alpha)
            
            cv2.circle(frame, (self.width // 2, y + 80), check_size, check_color, -1)
            
            # Draw checkmark symbol
            pts = np.array([
                [self.width // 2 - 20, y + 80],
                [self.width // 2 - 5, y + 95],
                [self.width // 2 + 25, y + 65]
            ], np.int32)
            cv2.polylines(frame, [pts], False, (0, 0, 0), 6)


# Export function to replace in animation_generator.py
def create_enhanced_video(topic: str, explanation: str, formulas: List[str] = None, 
                         video_id: str = None, videos_dir: Path = None) -> Optional[str]:
    """Create an enhanced educational video"""
    if videos_dir is None:
        from config import VIDEOS_DIR
        videos_dir = VIDEOS_DIR
    
    generator = EnhancedVideoGenerator(videos_dir)
    return generator.generate_video(topic, explanation, formulas, video_id, duration=15)