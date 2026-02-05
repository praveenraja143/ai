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
        Generate an AI image from text prompt using Google API
        """
        try:
            print(f"[AI IMAGE] Generating with Google AI mode '{self.model_name}': {prompt[:50]}...")
            
            # Note: The exact python syntax for Gemini image generation models 
            # might vary. If 'ImageGenerativeModel' is not available, we might need
            # to use a different approach. Standard approach for Imagen:
            try:
                model = genai.ImageGenerativeModel(self.model_name)
                response = model.generate_images(
                    prompt=prompt,
                    number_of_images=1,
                    aspect_ratio="1:1" if width==height else "16:9" 
                )
                if response and response.images:
                    image = response.images[0]
                else:
                    raise ValueError("No images returned from API")
            except Exception as e1:
                # Fallback to standard imagen if specific model fails
                print(f"[AI IMAGE] Specific model failed ({e1}), trying generic 'imagen-3.0-generate-001'...")
                model = genai.ImageGenerativeModel("imagen-3.0-generate-001")
                response = model.generate_images(prompt=prompt, number_of_images=1)
                image = response.images[0]

            # Save image
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            image.save(output_path)
            
            print(f"[AI IMAGE] Saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"[AI IMAGE] Error generating image via Google API: {e}")
            return None
    
    def generate_scene_images(self, answer_text: str, video_id: str, num_scenes: int = 3) -> list:
        """Generate multiple scene images from answer text"""
        try:
            # Create prompts
            prompts = self._create_scene_prompts(answer_text, num_scenes)
            
            # Generate images
            image_paths = []
            for i, prompt in enumerate(prompts):
                output_path = f"videos/frames/{video_id}_scene_{i}.png"
                path = self.generate_image(prompt, output_path)
                if path:
                    image_paths.append(path)
            
            return image_paths
            
        except Exception as e:
            print(f"[AI IMAGE] Error generating scene images: {e}")
            return []
    
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
