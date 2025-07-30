"""Main LottieAnimation QML component

Provides the primary QML component for Lottie animation playback.
"""

import os
from typing import Optional, List, Dict, Any
from ..compat import (
    QQuickPaintedItem, QObject, QUrl, QColor, QRectF, QPainter, QSize,
    signal, property_, slot,
    Status, CacheMode, Direction, FillMode
)
from ..rlottie.wrapper import RLottieWrapper, RLottieError
from .controller import AnimationController
from .cache import AnimationFrameCache

class LottieAnimation(QQuickPaintedItem):
    """QML component for Lottie animation playback"""
    
    # Signals
    started = signal()
    stopped = signal()
    finished = signal()
    position_changed = signal(float)
    frame_changed = signal(int)
    marker_reached = signal(str)
    error = signal(str)
    
    # Property notification signals
    status_changed = signal()
    cache_mode_changed = signal()
    source_changed = signal()
    playing_changed = signal()
    current_frame_changed = signal()
    progress_changed = signal()
    duration_changed = signal()
    position_changed_notify = signal()
    fill_mode_changed = signal()
    auto_play_changed = signal()
    playback_rate_changed = signal()
    loops_changed = signal()
    direction_changed = signal()
    tint_color_changed = signal()
    asynchronous_changed = signal()
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        
        # Initialize core components with error handling
        try:
            self._rlottie = RLottieWrapper()
        except RLottieError as e:
            print(f"Warning: RLottie not available: {e}")
            self._rlottie = None
        
        self._controller = AnimationController(self)
        self._cache = AnimationFrameCache()
        
        # Properties
        self._source = QUrl()
        self._status = Status.Null
        self._asynchronous = True
        self._cache_mode = CacheMode.CacheNone
        
        # Visual properties
        self._tint_color = QColor()
        self._fill_mode = FillMode.PreserveAspectFit
        self._smooth = True
        
        # Layer control
        self._visible_layers: List[str] = []
        self._layer_opacities: Dict[str, float] = {}
        
        # Connect controller signals
        self._controller.started.connect(self.started)
        self._controller.stopped.connect(self.stopped)
        self._controller.finished.connect(self.finished)
        self._controller.position_changed.connect(self.position_changed)
        self._controller.position_changed.connect(self.position_changed_notify)
        self._controller.frame_changed.connect(self.frame_changed)
        self._controller.frame_changed.connect(self.current_frame_changed)
        self._controller.frame_changed.connect(self.progress_changed)
        self._controller.marker_reached.connect(self.marker_reached)
        self._controller.error.connect(self.error)
        
        # Set frame callback for rendering
        self._controller.set_frame_callback(self._on_frame_changed)
        
        # Initialize property update timer (will be started when needed)
        self._property_update_timer = None
        
        # Enable antialiasing by default
        self.setAntialiasing(True)
        self.setRenderTarget(QQuickPaintedItem.RenderTarget.FramebufferObject)
    
    def paint(self, painter: QPainter) -> None:
        """Paint the current animation frame"""
        if not self._rlottie or not self._rlottie.is_loaded:
            return
        
        # Get current frame
        current_frame = self._controller.current_frame
        
        # Try to get from cache first
        image = self._cache.get_frame(current_frame)
        
        if image is None:
            # Render frame
            image = self._render_current_frame()
            if image is None:
                return
            
            # Cache the frame if appropriate
            self._cache.cache_frame(current_frame, image)
        
        # Calculate drawing rectangle based on fill mode
        source_rect = image.rect()
        target_rect = self._calculate_target_rect(source_rect)
        
        # Apply smoothing
        if self._smooth:
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Apply tint color if set
        if self._tint_color.isValid() and self._tint_color.alpha() > 0:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Multiply)
            painter.fillRect(target_rect, self._tint_color)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        
        # Draw the image - ensure compatible types for Qt6
        from ..compat import QRectF
        if hasattr(source_rect, 'toRectF'):
            # Convert QRect to QRectF if needed
            source_rect_f = source_rect.toRectF()
        else:
            # Create QRectF from QRect
            source_rect_f = QRectF(source_rect)
        
        painter.drawImage(target_rect, image, source_rect_f)
    
    def _render_current_frame(self) -> Optional[Any]:
        """Render the current frame using RLottie"""
        if not self._rlottie or not self._rlottie.is_loaded:
            return None
        
        # Set render size based on item size
        item_size = self.size()
        if item_size.width() <= 0 or item_size.height() <= 0:
            return None
        
        # Update RLottie render size
        self._rlottie.set_size(int(item_size.width()), int(item_size.height()))
        
        # Render frame
        return self._rlottie.render_frame(self._controller.current_frame)
    
    def _calculate_target_rect(self, source_rect: Any) -> QRectF:
        """Calculate target rectangle based on fill mode"""
        item_rect = QRectF(0, 0, self.width(), self.height())
        
        if self._fill_mode == FillMode.Stretch:
            return item_rect
        
        source_size = source_rect.size()
        target_size = item_rect.size()
        
        if source_size.width() <= 0 or source_size.height() <= 0:
            return item_rect
        
        # Calculate scale factors
        scale_x = target_size.width() / source_size.width()
        scale_y = target_size.height() / source_size.height()
        
        if self._fill_mode == FillMode.PreserveAspectFit:
            scale = min(scale_x, scale_y)
        else:  # PreserveAspectCrop
            scale = max(scale_x, scale_y)
        
        # Calculate scaled size
        scaled_width = source_size.width() * scale
        scaled_height = source_size.height() * scale
        
        # Center the image
        x = (target_size.width() - scaled_width) / 2
        y = (target_size.height() - scaled_height) / 2
        
        return QRectF(x, y, scaled_width, scaled_height)
    
    def _start_property_timer(self) -> None:
        """Start the property update timer if not already started"""
        if self._property_update_timer is None:
            try:
                from ..compat import QTimer
                self._property_update_timer = QTimer(self)
                self._property_update_timer.timeout.connect(self._emit_property_updates)
                self._property_update_timer.start(100)  # Update every 100ms
            except Exception as e:
                # Timer creation failed, continue without periodic updates
                print(f"Warning: Could not create property update timer: {e}")
    
    def _emit_property_updates(self) -> None:
        """Periodically emit property change signals for better QML binding"""
        if self._controller:
            # Only emit signals for frequently changing properties during playback
            if self._controller.playing:
                self.playing_changed.emit()
                self.position_changed_notify.emit()
                self.current_frame_changed.emit()
                self.progress_changed.emit()
    
    def _on_frame_changed(self, frame_num: int) -> None:
        """Handle frame change from controller"""
        # Trigger repaint
        self.update()
        
        # Handle pre-rendering for smooth playback
        if self._cache.cache_mode != CacheMode.CacheNone:
            frames_to_prerender = self._cache.get_prerender_frames(
                frame_num, 
                self._controller.playback_rate >= 0
            )
            
            # Pre-render frames in background (simplified - could be threaded)
            for prerender_frame in frames_to_prerender[:3]:  # Limit to 3 frames per update
                if not self._cache.has_frame(prerender_frame):
                    image = self._rlottie.render_frame(prerender_frame)
                    if image:
                        self._cache.cache_frame(prerender_frame, image)
    
    def _load_animation(self, source_path: str) -> None:
        """Load animation from file path"""
        if not os.path.exists(source_path):
            self._status = Status.Error
            self.error.emit(f"File not found: {source_path}")
            return
        
        try:
            # Check if RLottie is available
            if not self._rlottie:
                self._status = Status.Error
                self.status_changed.emit()
                self.error.emit("RLottie not available - install rlottie-python")
                return
            
            # Load animation
            if self._rlottie.load_from_file(source_path):
                # Set animation properties in controller
                self._controller.set_animation_properties(
                    self._rlottie.total_frames,
                    self._rlottie.frame_rate,
                    self._rlottie.duration
                )
                
                # Configure cache
                self._cache.set_animation_properties(
                    self._rlottie.total_frames,
                    hash(source_path)  # Use path hash as animation ID
                )
                self._cache.set_cache_mode(self._cache_mode)
                
                self._status = Status.Ready
                self.status_changed.emit()
                
                # Emit property change signals for loaded animation
                self.duration_changed.emit()
                self.current_frame_changed.emit()
                self.progress_changed.emit()
                self.position_changed_notify.emit()
                
                # Auto-play if enabled
                if self._controller.auto_play:
                    self.play()
                
            else:
                self._status = Status.Error
                self.status_changed.emit()
                self.error.emit("Failed to load animation")
                
        except RLottieError as e:
            self._status = Status.Error
            self.status_changed.emit()
            self.error.emit(str(e))
        except Exception as e:
            self._status = Status.Error
            self.status_changed.emit()
            self.error.emit(f"Unexpected error: {str(e)}")
    
    # Public methods (slots)
    @slot()
    def play(self) -> None:
        """Start animation playback"""
        self._start_property_timer()  # Start property updates when animation plays
        self._controller.play()
    
    @slot()
    def pause(self) -> None:
        """Pause animation playback"""
        self._controller.pause()
        self.playing_changed.emit()
    
    @slot()
    def stop(self) -> None:
        """Stop animation playback"""
        self._controller.stop()
        self.playing_changed.emit()
    
    @slot()
    def toggle(self) -> None:
        """Toggle between play and pause"""
        self._controller.toggle()
    
    @slot(float)
    def seek(self, position: float) -> None:
        """Seek to time position"""
        self._cache.optimize_for_seek(int(position * self._controller.frame_rate))
        self._controller.seek(position)
    
    @slot(int)
    def seek_to_frame(self, frame: int) -> None:
        """Seek to frame number"""
        self._cache.optimize_for_seek(frame)
        self._controller.seek_to_frame(frame)
    
    @slot(str)
    def seek_to_marker(self, marker_name: str) -> None:
        """Seek to named marker"""
        self._controller.seek_to_marker(marker_name)
    
    @slot(str)
    def show_layer(self, layer_name: str) -> None:
        """Show a specific layer"""
        if layer_name not in self._visible_layers:
            self._visible_layers.append(layer_name)
            self._cache.clear_cache()  # Clear cache as layers changed
            self.update()
    
    @slot(str)
    def hide_layer(self, layer_name: str) -> None:
        """Hide a specific layer"""
        if layer_name in self._visible_layers:
            self._visible_layers.remove(layer_name)
            self._cache.clear_cache()  # Clear cache as layers changed
            self.update()
    
    @slot(str, float)
    def set_layer_opacity(self, layer_name: str, opacity: float) -> None:
        """Set layer opacity"""
        opacity = max(0.0, min(1.0, opacity))
        self._layer_opacities[layer_name] = opacity
        self._cache.clear_cache()  # Clear cache as layers changed
        self.update()
    
    # Properties
    
    # Source
    def get_source(self) -> QUrl:
        return self._source
    
    def set_source(self, source: QUrl) -> None:
        if source != self._source:
            self._source = source
            self._status = Status.Loading
            self.source_changed.emit()
            self.status_changed.emit()
            
            if source.isLocalFile():
                self._load_animation(source.toLocalFile())
            elif source.toString():
                # Handle URL loading (could be implemented later)
                self._status = Status.Error
                self.status_changed.emit()
                self.error.emit("URL loading not yet implemented")
    
    source = property_(QUrl, get_source, set_source, notify=source_changed)
    
    # Status
    def get_status(self) -> int:
        return self._status
    
    status = property_(int, get_status, notify=status_changed)
    
    # Playing
    def get_playing(self) -> bool:
        return self._controller.playing
    
    def set_playing(self, playing: bool) -> None:
        if playing != self._controller.playing:
            self._controller.playing = playing
            self.playing_changed.emit()
    
    playing = property_(bool, get_playing, set_playing, notify=playing_changed)
    
    # Auto Play
    def get_auto_play(self) -> bool:
        return self._controller.auto_play
    
    def set_auto_play(self, auto_play: bool) -> None:
        if auto_play != self._controller.auto_play:
            self._controller.auto_play = auto_play
            self.auto_play_changed.emit()
    
    autoPlay = property_(bool, get_auto_play, set_auto_play, notify=auto_play_changed)
    
    # Playback Rate
    def get_playback_rate(self) -> float:
        return self._controller.playback_rate
    
    def set_playback_rate(self, rate: float) -> None:
        if rate != self._controller.playback_rate:
            self._controller.playback_rate = rate
            self.playback_rate_changed.emit()
    
    playbackRate = property_(float, get_playback_rate, set_playback_rate, notify=playback_rate_changed)
    
    # Loops
    def get_loops(self) -> int:
        return self._controller.loops
    
    def set_loops(self, loops: int) -> None:
        if loops != self._controller.loops:
            self._controller.loops = loops
            self.loops_changed.emit()
    
    loops = property_(int, get_loops, set_loops, notify=loops_changed)
    
    # Direction
    def get_direction(self) -> int:
        return self._controller.direction
    
    def set_direction(self, direction: int) -> None:
        if direction != self._controller.direction:
            self._controller.direction = direction
            self.direction_changed.emit()
    
    direction = property_(int, get_direction, set_direction, notify=direction_changed)
    
    # Position
    def get_position(self) -> float:
        return self._controller.position
    
    position = property_(float, get_position, notify=position_changed_notify)
    
    # Duration
    def get_duration(self) -> float:
        return self._controller.duration
    
    duration = property_(float, get_duration, notify=duration_changed)
    
    # Progress
    def get_progress(self) -> float:
        return self._controller.progress
    
    progress = property_(float, get_progress, notify=progress_changed)
    
    # Current Frame
    def get_current_frame(self) -> int:
        return self._controller.current_frame
    
    currentFrame = property_(int, get_current_frame, notify=current_frame_changed)
    
    # Cache Mode - define with explicit Qt Property for PySide6 compatibility
    def get_cache_mode(self) -> int:
        return self._cache_mode
    
    def set_cache_mode(self, mode: int) -> None:
        """Set cache mode with proper validation"""
        try:
            if mode != self._cache_mode:
                self._cache_mode = mode
                if hasattr(self._cache, 'set_cache_mode'):
                    self._cache.set_cache_mode(mode)
                self.cache_mode_changed.emit()
        except Exception as e:
            print(f"Error in set_cache_mode: {e}")
            # Continue with a safe fallback
            self._cache_mode = 0
    
    # Create property with explicit function binding to ensure proper resolution
    cacheMode = property_(int, get_cache_mode, set_cache_mode, notify=cache_mode_changed)
    
    # Tint Color
    def get_tint_color(self) -> QColor:
        return self._tint_color
    
    def set_tint_color(self, color: QColor) -> None:
        if color != self._tint_color:
            self._tint_color = color
            self.tint_color_changed.emit()
            self.update()
    
    tintColor = property_(QColor, get_tint_color, set_tint_color, notify=tint_color_changed)
    
    # Fill Mode
    def get_fill_mode(self) -> int:
        return self._fill_mode
    
    def set_fill_mode(self, mode: int) -> None:
        """Set fill mode with proper validation"""
        try:
            if mode != self._fill_mode:
                self._fill_mode = mode
                self.fill_mode_changed.emit()
                self.update()
        except Exception as e:
            print(f"Error in set_fill_mode: {e}")
            # Continue with a safe fallback
            self._fill_mode = 0
    
    # Create property with explicit function binding to ensure proper resolution
    fillMode = property_(int, get_fill_mode, set_fill_mode, notify=fill_mode_changed)
    
    # Smooth
    def get_smooth(self) -> bool:
        return self._smooth
    
    def set_smooth(self, smooth: bool) -> None:
        if smooth != self._smooth:
            self._smooth = smooth
            self.update()
    
    smooth = property_(bool, get_smooth, set_smooth)
    
    # Asynchronous
    def get_asynchronous(self) -> bool:
        return self._asynchronous
    
    def set_asynchronous(self, async_: bool) -> None:
        if async_ != self._asynchronous:
            self._asynchronous = async_
            self.asynchronous_changed.emit()
    
    asynchronous = property_(bool, get_asynchronous, set_asynchronous, notify=asynchronous_changed)