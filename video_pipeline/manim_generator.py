import google.generativeai as genai
import os
import subprocess
import logging
from pathlib import Path
from config import GEMINI_CONFIG, VIDEOS_DIR

# Configure logging
logger = logging.getLogger(__name__)

class ManimCodeGenerator:
    """
    Generates educational videos using Manim (Mathematical Animation Engine)
    powered by Gemini code generation.
    """
    
    def __init__(self):
        self.api_key = GEMINI_CONFIG["api_key"]
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(GEMINI_CONFIG["model"])
        
        # Configure FFmpeg path explicitly for Manim
        from manim import config
        import shutil
        
        if not shutil.which("ffmpeg"):
            # Try to locate it in common Winget location
            ffmpeg_path = r"C:\Users\pk\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"
            if os.path.exists(ffmpeg_path):
                print(f"[MANIM] FFmpeg found at {ffmpeg_path}, configuring...")
                config.ffmpeg_executable = ffmpeg_path
                # Also add to PATH for subprocess calls
                os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)
            else:
                 print("[MANIM] WARNING: FFmpeg not found in path or default location.")
        
    def generate_video(self, topic: str, explanation: str, video_id: str) -> str:
        """
        Main pipeline: Generate Manim code -> Render video
        """
        try:
            print(f"[MANIM] Generating code for: {topic}")
            manim_code = self._generate_manim_code(topic, explanation)
            
            if not manim_code:
                print("[MANIM] Failed to generate code")
                return None
                
            return self._render_manim(manim_code, video_id)
            
        except Exception as e:
            print(f"[MANIM] Error in generation pipeline: {e}")
            return None

    def _generate_manim_code(self, topic: str, explanation: str) -> str:
        """
        Prompt Gemini to write a robust Manim script
        """
        prompt = f"""
        Act as an expert Manim (Python) developer.
        Write a COMPLETE, RUNNABLE Manim script to explain this concept:
        
        Topic: {topic}
        Explanation: {explanation[:800]} of the core concept.
        
        Requirements:
        1. Class name MUST be 'ConceptScene'.
        2. Use ONLY 'Text' class for text (Do NOT use Tex or MathTex as LaTeX is not installed).
        3. Use simple, clear visualizations:
           - Shapes (Circle, Square, Rectangle)
           - Arrows to show flow
           - Transform animations (Transform, FadeIn, Write)
           - Colors (BLUE, RED, GREEN, YELLOW)
        4. Structure:
           - Show Topic Title.
           - Animate visuals explaining the concept step-by-step.
           - Show a brief conclusion.
        5. Code MUST include imports: `from manim import *`
        6. DO NOT use external assets (images/svgs). Use only built-in Manim shapes.
        7. NO markdown backticks. Just pure Python code.
        
        Output valid Python code only.
        """
        
        try:
            response = self.model.generate_content(prompt)
            code = response.text.strip()
            # Clean markdown if present
            code = code.replace("```python", "").replace("```", "").strip()
            return code
        except Exception as e:
            print(f"[MANIM] Generator error: {e}")
            return None

    def _render_manim(self, code: str, video_id: str) -> str:
        """
        Save code and execute Manim to render video
        """
        # Save code to valid file
        scene_file = Path(VIDEOS_DIR) / f"manim_{video_id}.py"
        output_dir = Path(VIDEOS_DIR) 
        
        with open(scene_file, "w") as f:
            f.write(code)
            
        print(f"[MANIM] Saved script to {scene_file}")
        
        # Build command: manim -qm --media_dir ...
        # -ql = Low quality (480p) for speed, -qm = Medium (720p)
        cmd = [
            "manim",
            "-ql",  # Use Low quality for speed testing first, or -qm
            "--media_dir", str(output_dir),
            "-o", f"{video_id}.mp4", # Output filename
            str(scene_file),
            "ConceptScene"
        ]
        
        print(f"[MANIM] Rendering video... (This may take time)")
        try:
            # Run manim command
            process = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                timeout=300 # 5 min timeout
            )
            
            if process.returncode != 0:
                print(f"[MANIM] Render failed:\n{process.stderr}")
                return None
                
            # Manim output structure is typically: media_dir/videos/scene_file_name/quality/filename.mp4
            # Or with -o it tries to place it specific.
            # Default structure: {media_dir}/videos/{script_name}/480p15/ConceptScene.mp4
            # Let's try to locate the file.
            
            # Since we specified -o video_id.mp4, Manim places it in:
            # media_dir/videos/manim_{video_id}/480p15/{video_id}.mp4 
            # We need to find where it actually landed.
            
            # Simple finder:
            expected_path = output_dir / "videos" / f"manim_{video_id}" / "480p15" / f"{video_id}.mp4"
            if expected_path.exists():
                # Move to main videos dir for serving
                final_path = output_dir / f"{video_id}.mp4"
                import shutil
                shutil.move(str(expected_path), str(final_path))
                print(f"[MANIM] Video moved to {final_path}")
                return str(final_path)
            
            # Search recursively if path logic failed
            found = list(output_dir.rglob(f"{video_id}.mp4"))
            if found:
                final_path = output_dir / f"{video_id}.mp4"
                import shutil
                shutil.move(str(found[0]), str(final_path))
                return str(final_path)
                
            print("[MANIM] Video file not found after success return code")
            return None
            
        except subprocess.TimeoutExpired:
            print("[MANIM] Render timed out")
            return None
        except Exception as e:
            print(f"[MANIM] Execution error: {e}")
            return None
