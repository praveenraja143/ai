"""
Progress Tracker - Tracks video generation progress
"""


class ProgressTracker:
    """Tracks the progress of video generation"""
    
    def __init__(self):
        self.current_scene = 0
        self.total_scenes = 0
        self.percentage = 0
        self.status = "idle"  # idle, processing, completed, failed
    
    def start(self, total_scenes: int):
        """Start tracking progress"""
        self.total_scenes = total_scenes
        self.current_scene = 0
        self.percentage = 0
        self.status = "processing"
    
    def update(self, current: int, total: int):
        """Update progress"""
        self.current_scene = current
        self.total_scenes = total
        self.percentage = int((current / total) * 100) if total > 0 else 0
        self.status = "processing"
    
    def complete(self):
        """Mark as completed"""
        self.percentage = 100
        self.status = "completed"
    
    def fail(self, error: str = None):
        """Mark as failed"""
        self.status = "failed"
        self.error = error
    
    def get_status(self) -> dict:
        """Get current status as dictionary"""
        return {
            "current_scene": self.current_scene,
            "total_scenes": self.total_scenes,
            "percentage": self.percentage,
            "status": self.status
        }
