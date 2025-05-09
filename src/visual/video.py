import cv2
import torch
import numpy as np
from typing import List, Dict, Any
from dataclasses import dataclass
from src.logger import setup_logger

from src.struct.frame import Frame
from src.struct.utils import annotate_frame_with_detections

@dataclass
class VideoFrame:
    """Encapsulate a single video frame with annotations."""
    frame_id: int
    timestamp: float
    image: np.ndarray
    detections: List[Dict[str, Any]]


class VideoVisualizer:
    def __init__(
            self, 
            initial_frame: np.ndarray, 
            class_names: Dict[int, str] = None,
            window_name: str = "Video Visualizer"
            ):
        super().__init__()
        
        self.class_names = class_names if class_names is not None else {}
        self.window_name = window_name
        self.logger = setup_logger("api.log")
        
        prepared = self._prepare_frame(initial_frame)
        self.frame = Frame(prepared)
        
        # color for each class
        self.color_dict = {
            0: (255, 255, 255),  # ball       : white
            1: (  0,   0, 255),  # goalkeeper : blue
            2: (  0, 255,   0),  # player     : green
            3: (255, 165,   0),  # referee    : orange
        }

    def update(self, video_frame: VideoFrame) -> None:
        """Updates the visualizer with a new frame and applies annotations."""
        prepared = self._prepare_frame(video_frame.image)
        self.frame = Frame(prepared, metadata={"class_names":self.class_names})
        self.frame = annotate_frame_with_detections(self.frame, video_frame.detections)


    def resize_to_width(self, new_width: int):
        current_width = self.frame.current_width
        if current_width <= 0:
            return
        
        scale_factor = float(new_width) / float(current_width)
        old_scale = self.frame._scale
        self.frame.update_scale(old_scale * scale_factor)


    def clear_annotations(self) -> None:
        if isinstance(self.frame, Frame):
            self.frame.clear_annotations()


    def show(self) -> None:
        """Displays the annotated frame."""
        cv2.imshow(self.window_name, self.frame)
        cv2.waitKey(1)

    def get_image(self) -> np.ndarray:
        """Returns the annotated frame as a NumPy array."""
        return self.frame.data.image
    

    def _prepare_frame(self, frame: np.ndarray) -> np.ndarray:
        """Converts the frame into OpenCV format."""
        if isinstance(frame, torch.Tensor):
            frame = frame.cpu().numpy()
            frame = (frame * 255).clip(0, 255).astype(np.uint8)

        if frame.dtype != np.uint8:
            frame = frame.clip(0, 255).astype(np.uint8)

        if frame.shape[-1] == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        return frame