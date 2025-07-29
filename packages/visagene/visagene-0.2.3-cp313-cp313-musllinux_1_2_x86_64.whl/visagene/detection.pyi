from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import onnxruntime as onnxruntime
import os as os
import pixtreme as px
import tensorrt as trt
import typing
import visagene.base
from visagene.base import BaseModelLoader
from visagene.schema import VisageneFace
__all__ = ['BaseFaceDetector', 'BaseModelLoader', 'OnnxFaceDetector', 'TrtFaceDetector', 'VisageneFace', 'cp', 'onnxruntime', 'os', 'px', 'trt']
class BaseFaceDetector(visagene.base.BaseModelLoader):
    """
    
        Base class for face detection models.
    
        Detects faces in images and returns bounding boxes, keypoints,
        and confidence scores for identified faces.
        
    """
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda') -> None:
        ...
    def crop(self, image: cp.ndarray, kps: cp.ndarray, size: int = 512) -> tuple[cp.ndarray, cp.ndarray]:
        """
        Crop face image using keypoints
        """
    def distance2bbox(self, points: cp.ndarray, distance: cp.ndarray, max_shape = None) -> cp.ndarray:
        """
        Convert distance predictions to bounding boxes
        """
    def distance2kps(self, points: cp.ndarray, distance: cp.ndarray, max_shape = None) -> cp.ndarray:
        """
        Convert distance predictions to keypoints
        """
    def forward(self, image: cp.ndarray, threshold: float) -> tuple[list[cp.ndarray], list[cp.ndarray], list[cp.ndarray]]:
        """
        
                Placeholder for the forward method.
                
        """
    def get(self, image: cp.ndarray, crop_size: int = 512, max_num: int = 0, metric: str = 'default') -> list[VisageneFace]:
        ...
    def nms(self, dets: cp.ndarray):
        """
        Non-Maximum Suppression
        """
class OnnxFaceDetector(BaseFaceDetector):
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda') -> None:
        ...
    def forward(self, image: cp.ndarray, threshold: float) -> tuple[list[cp.ndarray], list[cp.ndarray], list[cp.ndarray]]:
        ...
    def initialize(self, model_bytes: bytes, device: str, device_id: str = '0') -> None:
        ...
class TrtFaceDetector(BaseFaceDetector):
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda') -> None:
        ...
    def forward(self, image: cp.ndarray, threshold: float) -> tuple[list[cp.ndarray], list[cp.ndarray], list[cp.ndarray]]:
        """
        Forward pass using TensorRT
        """
    def initialize(self, model_bytes: bytes, device: str, device_id: str) -> None:
        ...
__test__: dict = {}
