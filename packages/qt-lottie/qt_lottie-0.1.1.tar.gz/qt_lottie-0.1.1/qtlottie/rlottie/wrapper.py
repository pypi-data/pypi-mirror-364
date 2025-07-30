"""RLottie integration wrapper

Provides a Python interface to the RLottie library for rendering Lottie animations.
"""

import os
from typing import Optional, Tuple, Any
from ..compat import QImage, QSize

try:
    import rlottie_python as rlottie
    RLOTTIE_AVAILABLE = True
except ImportError:
    try:
        import rlottie
        RLOTTIE_AVAILABLE = True
    except ImportError:
        RLOTTIE_AVAILABLE = False
        rlottie = None

class RLottieError(Exception):
    """Exception raised for RLottie-related errors"""
    pass

class RLottieWrapper:
    """Wrapper around RLottie animation rendering"""
    
    def __init__(self):
        if not RLOTTIE_AVAILABLE:
            raise RLottieError(
                "rlottie-python not found. Install with: pip install rlottie-python"
            )
        
        self.animation: Optional[Any] = None
        self._width = 0
        self._height = 0
        self._total_frames = 0
        self._frame_rate = 30.0
        self._duration = 0.0
        self._surface: Optional[Any] = None
    
    def load_from_file(self, file_path: str) -> bool:
        """Load animation from file
        
        Args:
            file_path: Path to the Lottie JSON file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        if not os.path.exists(file_path):
            return False
            
        try:
            self.animation = rlottie.LottieAnimation.from_file(file_path)
            if not self.animation:
                return False
                
            # Get animation properties
            self._total_frames = self.animation.lottie_animation_get_totalframe()
            self._frame_rate = self.animation.lottie_animation_get_framerate()
            self._duration = self.animation.lottie_animation_get_duration()
            
            # Get default size
            width, height = self.animation.lottie_animation_get_size()
            self._width = int(width)
            self._height = int(height)
            
            return True
            
        except Exception:
            return False
    
    def load_from_data(self, json_data: str, resource_path: str = "") -> bool:
        """Load animation from JSON data
        
        Args:
            json_data: Lottie animation JSON string
            resource_path: Base path for resources
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            self.animation = rlottie.LottieAnimation.from_data(json_data)
            if not self.animation:
                return False
                
            # Get animation properties
            self._total_frames = self.animation.lottie_animation_get_totalframe()
            self._frame_rate = self.animation.lottie_animation_get_framerate()
            self._duration = self.animation.lottie_animation_get_duration()
            
            # Get default size
            width, height = self.animation.lottie_animation_get_size()
            self._width = int(width)
            self._height = int(height)
            
            return True
            
        except Exception:
            return False
    
    def set_size(self, width: int, height: int) -> None:
        """Set render size
        
        Args:
            width: Render width in pixels
            height: Render height in pixels
        """
        self._width = max(1, width)
        self._height = max(1, height)
    
    def render_frame(self, frame_number: int) -> Optional[QImage]:
        """Render a specific frame
        
        Args:
            frame_number: Frame number to render (0-based)
            
        Returns:
            QImage with rendered frame, or None if failed
        """
        if not self.animation:
            return None
            
        if frame_number < 0 or frame_number >= self._total_frames:
            return None
            
        try:
            # Render frame using rlottie-python API
            pil_image = self.animation.render_pillow_frame(frame_num=frame_number, width=self._width, height=self._height)
            
            # Convert PIL Image to QImage
            return self._pil_to_qimage(pil_image)
            
        except Exception:
            return None
    
    def render_frame_at_pos(self, position: float) -> Optional[QImage]:
        """Render frame at specific time position
        
        Args:
            position: Time position in seconds
            
        Returns:
            QImage with rendered frame, or None if failed
        """
        if self._duration <= 0:
            return None
            
        # Convert position to frame number
        frame = int(position * self._frame_rate)
        frame = max(0, min(frame, self._total_frames - 1))
        
        return self.render_frame(frame)
    
    def _pil_to_qimage(self, pil_image) -> QImage:
        """Convert PIL Image to QImage"""
        if not pil_image:
            return QImage()
        
        # Convert PIL image to bytes
        import io
        bytes_io = io.BytesIO()
        pil_image.save(bytes_io, format='PNG')
        image_bytes = bytes_io.getvalue()
        
        # Create QImage from bytes
        image = QImage()
        image.loadFromData(image_bytes)
        
        return image
    
    @property
    def total_frames(self) -> int:
        """Total number of frames in animation"""
        return self._total_frames
    
    @property
    def frame_rate(self) -> float:
        """Animation frame rate"""
        return self._frame_rate
    
    @property
    def duration(self) -> float:
        """Animation duration in seconds"""
        return self._duration
    
    @property
    def size(self) -> Tuple[int, int]:
        """Animation default size (width, height)"""
        return (self._width, self._height)
    
    @property
    def is_loaded(self) -> bool:
        """Check if animation is loaded"""
        return self.animation is not None

def is_rlottie_available() -> bool:
    """Check if RLottie is available"""
    return RLOTTIE_AVAILABLE

def get_rlottie_version() -> str:
    """Get RLottie version string"""
    if not RLOTTIE_AVAILABLE:
        return "Not available"
    try:
        return getattr(rlottie, '__version__', 'Unknown')
    except:
        return "Unknown"