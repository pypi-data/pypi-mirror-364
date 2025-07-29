import cupy as cp
import onnxruntime
import pixtreme as px

from .base import BaseModelLoader


class BaseSegmentation(BaseModelLoader):
    """
    Base class for face segmentation models.

    Segments facial regions like eyes, nose, mouth, and skin
    to enable targeted operations like face swapping and enhancement.
    """

    def __init__(
        self,
        model_path: str | None = None,
        model_bytes: bytes | None = None,
        device: str = "cuda",
    ) -> None:
        super().__init__(model_path, model_bytes, device)

        # Face segmentation parameters
        self.input_size = (512, 512)
        self.input_mean = (0.485, 0.456, 0.406)
        self.input_std = (0.229, 0.224, 0.225)

        self.indexes = [
            [1, 3, 14, 15, 16, 17, 18],  # Outer face
            [2, 4, 5],  # Skin
            [6, 7, 8, 9, 10, 11, 12, 13],  # Facial features
        ]
        self.num_categories = len(self.indexes)

        # Create all indices and category mapping
        all_indices = []
        category_ids = []
        for cat_idx, index_list in enumerate(self.indexes):
            all_indices.extend(index_list)
            category_ids.extend([cat_idx] * len(index_list))

        self.all_indices = cp.array(all_indices)  # All class indices
        self.category_ids = cp.array(category_ids)  # Corresponding category IDs

    def forward(self, images: list[cp.ndarray]) -> cp.ndarray:
        """
        Placeholder for the forward method.
        """
        # Must be implemented by subclasses
        raise NotImplementedError("forward method must be implemented in subclass")

    def get(self, image: cp.ndarray) -> cp.ndarray:
        """
        Face segmentation method for a single image.
        """
        masks = self.forward([image])  # Ensure model is loaded

        return masks[0]

    def batch_get(self, images: list[cp.ndarray], MAX_BATCH_SIZE: int = 16) -> list[cp.ndarray]:
        """
        Face segmentation inference method.
        Common implementation shared by Onnx and Trt versions.
        Supports batch processing for multiple images.
        """

        # Split processing if batch size is too large
        if len(images) > MAX_BATCH_SIZE:
            results = []
            for i in range(0, len(images), MAX_BATCH_SIZE):
                batch_images = images[i : i + MAX_BATCH_SIZE]
                batch_results = self.forward(batch_images)
                results.extend(batch_results)
            return results
        else:
            return self.forward(images)

    def composite_masks(self, preds: cp.ndarray) -> cp.ndarray:
        """
        Composite masks into a single image.
        """
        # Stack masks along the channel dimension
        # Adjust if preds has shape (1, N, 19, 512, 512)
        if preds.ndim == 5 and preds.shape[0] == 1:
            preds = preds[0]  # (N, 19, 512, 512)

        batch_size = preds.shape[0]

        # Calculate softmax for entire batch
        # exp(x - max) / sum(exp(x - max)) for numerical stability
        max_vals = cp.max(preds, axis=1, keepdims=True)  # (N, 1, 512, 512)
        exp_vals = cp.exp(preds - max_vals)
        prob = exp_vals / cp.sum(exp_vals, axis=1, keepdims=True)  # (N, 19, 512, 512)

        # Calculate argmax for entire batch
        pred = cp.argmax(prob, axis=1)  # (N, 512, 512)

        # Vectorized processing for entire batch
        # Execute all comparisons at once
        pred_expanded = pred[..., cp.newaxis]  # (N, 512, 512, 1)

        # Expand indices to batch dimension
        indices_expanded = self.all_indices[cp.newaxis, cp.newaxis, cp.newaxis, :]  # (1, 1, 1, num_all_indices)

        # Calculate all class matches at once
        all_matches = (pred_expanded == indices_expanded).astype(cp.float32)  # (N, 512, 512, num_all_indices)

        # Create category masks at once
        category_masks = cp.arange(self.num_categories)[:, cp.newaxis] == self.category_ids[cp.newaxis, :]

        # Aggregate by category using Einstein summation
        # all_matches: (N, 512, 512, num_all_indices), category_masks: (3, num_all_indices)
        # Calculate and aggregate masks for each category
        _masks = cp.einsum("nijk,mk->mnijk", all_matches, category_masks.astype(cp.float32))
        _masks = cp.sum(_masks, axis=-1)  # (3, N, 512, 512)

        # Combine masks for each batch
        masks_list = []
        for n in range(batch_size):
            # Stack 3 category masks for each batch
            # _masks[i, n] has shape (512, 512)
            mask = cp.stack([_masks[0, n], _masks[1, n], _masks[2, n]], axis=0)  # (3, 512, 512)
            masks_list.append(mask)

        # Combine along batch dimension
        masks = cp.stack(masks_list, axis=0)  # (N, 3, 512, 512)

        return masks


class OnnxSegmentation(BaseSegmentation):
    """Face segmentation using ONNX Runtime for inference."""

    def __init__(
        self,
        model_path: str | None = None,
        model_bytes: bytes | None = None,
        device: str = "cuda",
    ) -> None:
        super().__init__(model_path, model_bytes, device)

        if self.model_bytes is None and self.model_path is not None:
            with open(self.model_path, "rb") as f:
                self.model_bytes = f.read()

        assert self.model_bytes is not None, "model_bytes must be provided if model_path is not specified"
        self.initialize(self.model_bytes, self.device, self.device_id)

    def initialize(self, model_bytes: bytes, device: str, device_id: str = "0") -> None:
        onnxruntime.preload_dlls()
        sees_options = onnxruntime.SessionOptions()
        sees_options.log_severity_level = 4
        sees_options.log_verbosity_level = 4

        provider_options = [{}]
        if "cuda" in device:
            providers = ["CUDAExecutionProvider"]
            provider_options = [{"device_id": device_id}]
        else:
            providers = ["CPUExecutionProvider"]

        onnx_params = {
            "session_options": sees_options,
            "providers": providers,
            "provider_options": provider_options,
        }

        self.session = onnxruntime.InferenceSession(model_bytes, **onnx_params)
        self.input_name = self.session.get_inputs()[0].name
        self.input_shape = self.session.get_inputs()[0].shape
        self.dtype = self.session.get_inputs()[0].type
        self.output_shape = self.session.get_outputs()[0].shape
        self.output_name = self.session.get_outputs()[0].name

    def forward(self, images: list[cp.ndarray]) -> list[cp.ndarray]:
        batch = px.images_to_batch(
            images,
            scalefactor=1.0 / cp.asarray(self.input_std),
            size=self.input_size,
            mean=self.input_mean,
            swap_rb=True,
            layout="HWC",
        )

        batch_numpy = cp.asnumpy(batch)
        preds = self.session.run(None, {self.input_name: batch_numpy})
        preds = cp.asarray(preds)
        masks = self.composite_masks(preds)  # (N, 3, 512, 512)
        masks_list = px.batch_to_images(masks, swap_rb=True, layout="NCHW")

        return masks_list
