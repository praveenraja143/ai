"""
AI Image Generator - Uses Stable Diffusion to generate images from text
"""
import os
from PIL import Image

# Try to import AI libraries, handle errors gracefully
try:
    import torch
    from diffusers import StableDiffusionPipeline
    AI_LIBS_AVAILABLE = True
except (ImportError, AttributeError) as e:
    print(f"[AI IMAGE] Could not load AI libraries: {e}")
    AI_LIBS_AVAILABLE = False
    torch = None
    StableDiffusionPipeline = None


class AIImageGenerator:
    """Generates AI images using Stable Diffusion"""
    
    def __init__(self):
        self.pipe = None
        self.model_loaded = False
        
    def load_model(self):
        """Load Stable Diffusion model (lazy loading)"""
        if self.model_loaded:
            return
        
        if not AI_LIBS_AVAILABLE:
            print("[AI IMAGE] AI libraries not available, cannot load model")
            return
            
        try:
            print("[AI IMAGE] Loading Stable Diffusion model...")
            # Use a smaller, faster model for CPU
            model_id = "runwayml/stable-diffusion-v1-5"
            
            # Check if CUDA is available
            if torch.cuda.is_available():
                print("[AI IMAGE] Using GPU acceleration")
                self.pipe = StableDiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16
                )
                self.pipe = self.pipe.to("cuda")
            else:
                print("[AI IMAGE] Using CPU (this will be slower)")
                self.pipe = StableDiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float32
                )
                # Enable CPU optimizations
                self.pipe.enable_attention_slicing()
            
            self.model_loaded = True
            print("[AI IMAGE] Model loaded successfully")
            
        except Exception as e:
            print(f"[AI IMAGE] Error loading model: {e}")
            self.model_loaded = False
            raise
    
    def generate_image(self, prompt: str, output_path: str, width: int = 512, height: int = 512) -> str:
        """
        Generate an AI image from text prompt
        
        Args:
            prompt: Text description of the image
            output_path: Path to save the generated image
            width: Image width (default 512)
            height: Image height (default 512)
            
        Returns:
            Path to the generated image
        """
        try:
            # Load model if not already loaded
            if not self.model_loaded:
                self.load_model()
            
            print(f"[AI IMAGE] Generating: {prompt[:50]}...")
            
            # Generate image
            image = self.pipe(
                prompt,
                num_inference_steps=20,  # Fewer steps for faster generation
                guidance_scale=7.5,
                width=width,
                height=height
            ).images[0]
            
            # Save image
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            image.save(output_path)
            
            print(f"[AI IMAGE] Saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"[AI IMAGE] Error generating image: {e}")
            return None
    
    def generate_scene_images(self, answer_text: str, video_id: str, num_scenes: int = 3) -> list:
        """
        Generate multiple scene images from answer text
        
        Args:
            answer_text: The answer text to visualize
            video_id: Unique identifier for the video
            num_scenes: Number of scenes to generate
            
        Returns:
            List of paths to generated images
        """
        try:
            # Create prompts for different scenes
            prompts = self._create_scene_prompts(answer_text, num_scenes)
            
            # Generate images for each scene
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
        """
        Create scene prompts from answer text
        
        Args:
            answer_text: The answer text
            num_scenes: Number of scenes to create
            
        Returns:
            List of prompts for each scene
        """
        # Extract key concepts from answer
        # This is a simple implementation - can be enhanced with LLM
        
        # For now, create generic educational scene prompts
        base_prompt = "educational illustration, professional, detailed, "
        
        prompts = [
            base_prompt + "introduction scene, title card, clean design",
            base_prompt + "main concept visualization, diagram, clear explanation",
            base_prompt + "conclusion scene, summary, professional"
        ]
        
        return prompts[:num_scenes]
