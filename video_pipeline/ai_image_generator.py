"""
AI Image Generator - Uses Google Gemini/Imagen to generate images from text
"""
import os
import google.generativeai as genai
from PIL import Image
from config import GEMINI_CONFIG

# We no longer need local torch/diffusers
AI_LIBS_AVAILABLE = True  # We use API now

class AIImageGenerator:
    """Generates AI images using Google's Generative AI"""
    
    def __init__(self):
        self.api_key = GEMINI_CONFIG["api_key"]
        try:
            genai.configure(api_key=self.api_key)
            # Try the specific image generation model found in user's list
            # or default to a known imagen check
            self.model_name = "gemini-2.0-flash-exp-image-generation" 
            print(f"[AI IMAGE] Initialized using Google API model: {self.model_name}")
        except Exception as e:
            print(f"[AI IMAGE] Failed to configure Google API: {e}")

    def load_model(self):
        """No-op for API based generator"""
        pass
    
    def generate_image(self, prompt: str, output_path: str, width: int = 1024, height: int = 1024) -> str:
        """
        Generate an AI image from text prompt using Pollinations.ai (Free, High Quality)
        """
        try:
            print(f"[AI IMAGE] Generating with Pollinations AI: {prompt[:50]}...")
            
            # Use Pollinations.ai (No API key required, reliable free tier)
            import requests
            import time
            from urllib.parse import quote
            
            # Encode prompt
            encoded_prompt = quote(prompt)
            url = f"https://pollinations.ai/p/{encoded_prompt}?width={width}&height={height}&seed={int(time.time())}&model=flux"
            
            # Download image
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                # Save image
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                    
                print(f"[AI IMAGE] Saved to: {output_path}")
                return output_path
            else:
                print(f"[AI IMAGE] Pollinations API failed: {response.status_code}")
                raise Exception("Pollinations API failed")
            
        except Exception as e:
            print(f"[AI IMAGE] Error generating image: {e}")
            # Even if API fails, return a synthetic image so video creation works
            try:
                # Fallback: Create a beautiful synthetic image using PIL
                print("[AI IMAGE] Fallback... Creating synthetic scene...")
                import random
                from PIL import ImageDraw, ImageFont
                
                # Create abstract art background
                img = Image.new('RGB', (width, height), color=(10, 10, 25))
                draw = ImageDraw.Draw(img)
                
                # Draw random "bokeh" circles for style
                for _ in range(20):
                    x = random.randint(0, width)
                    y = random.randint(0, height)
                    r = random.randint(50, 300)
                    color = (random.randint(50, 255), random.randint(50, 255), random.randint(100, 255), 100)
                    draw.ellipse((x-r, y-r, x+r, y+r), fill=color)
                
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                img.save(output_path)
                return output_path
            except:
                return None
    
    def generate_scene_images(self, answer_text: str, video_id: str, num_scenes: int = 3) -> list:
        """Generate multiple scene images from answer text"""
        try:
            # Create prompts
            prompts = self._create_scene_prompts(answer_text, num_scenes)
            return self.generate_images_from_list(prompts, video_id)
            
        except Exception as e:
            print(f"[AI IMAGE] Error generating scene images: {e}")
            return []

    def generate_images_from_list(self, prompts: list, video_id: str) -> list:
        """Generate images from a list of prompts"""
        image_paths = []
        for i, prompt in enumerate(prompts):
            output_path = f"videos/frames/{video_id}_scene_{i}.png"
            path = self.generate_image(prompt, output_path)
            if path:
                image_paths.append(path)
        return image_paths
    
    def _create_scene_prompts(self, answer_text: str, num_scenes: int) -> list:
        """Create descriptive prompts using Gemini Text model"""
        try:
            model = genai.GenerativeModel("gemini-1.5-flash") # Use flash for prompt Gen
            
            # Updated Prompt for Storytelling style
            prompt = f"""
            You are a creative director for a 3D animated educational short.
            Create {num_scenes} sequential image prompts to visualize this concept:
            Concept: "{answer_text[:500]}..."
            
            Style Guide: 
            - 3D Pixar/Disney style animation, vibrant colors, expressive characters.
            - Cute, friendly atmosphere.
            - High quality 3D render, raytracing, 4k.
            
            Sequence:
            1. Scene 1: An engaging opening shot introducing the topic (visual metaphor).
            2. Scene 2: The core action or mechanism explaining HOW it works.
            3. Scene 3: A fun conclusion or real-world application.
            
            Format: Just the visual description per line. No labels.
            """
            response = model.generate_content(prompt)
            lines = [l.strip() for l in response.text.strip().split('\n') if l.strip()]
            return lines[:num_scenes]
        except:
             # Fallback
             base = "3d pixar style educational animation, cute, vibrant, 4k render of: "
             return [f"{base} {answer_text[:50]} scene {i+1}" for i in range(num_scenes)]
