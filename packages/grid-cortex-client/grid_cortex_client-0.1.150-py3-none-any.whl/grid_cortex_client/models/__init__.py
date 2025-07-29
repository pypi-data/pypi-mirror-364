"""Models for interacting with specific Cortex deployments."""
from .base_model import BaseModel
from .depth import DepthModel 
from .detection import DetectionModel
from .segmentation import SegmentationModel, SAM2Model
from .vlm import VLMModel, MoonDreamModel  # Importing the VLMModel and MoonDreamModel for Vision Language Models
from .matching import MatchingModel  # Importing the MatchingModel for image matching
from .grasp import GraspModel

__all__ = [
    "BaseModel",
    "DepthModel",
    "DetectionModel",
    "SegmentationModel",
    "SAM2Model",
    "MatchingModel",  # Including MatchingModel in the public API
    "VLMModel",  # Including VLMModel in the public API
    "GraspModel",
    "MoonDreamModel",  # Assuming MoonDreamModel is a specific VLMModel
]

