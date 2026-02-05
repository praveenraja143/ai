# Test script for video generation
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(os.getcwd())

from video_pipeline.video_generator import generate_video
from video_pipeline.script_generator import generate_script

# Test content
topic = "Newton's Second Law"
text = """Newton's Second Law states that Force equals Mass times Acceleration.
F = m * a

This means that if you push an object with more force, it accelerates faster.
If the object is heavier (more mass), it accelerates slower for the same force.

Example:
If Mass = 10 kg and Acceleration = 5 m/s^2, then:
Force = 10 * 5 = 50 Newtons.
"""

print("Generating script...")
scenes = generate_script(text)
print(f"Generated {len(scenes)} scenes")

print("Generating video...")
video_path = generate_video(scenes, "test_video_1080p")
print(f"Video generated at: {video_path}")

# Verify file exists and size
if os.path.exists(video_path):
    size_mb = os.path.getsize(video_path) / (1024 * 1024)
    print(f"File size: {size_mb:.2f} MB")
    print("Test PASSED")
else:
    print("Test FAILED: File not found")
