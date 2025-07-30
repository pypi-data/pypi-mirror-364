import logging
from typing import List, Tuple, TypedDict

import cv2
import numpy as np
import onnxruntime as ort
from PIL.Image import Image
from tqdm.auto import trange

from anomalytda_client.internal._model import BaseModel

logger = logging.getLogger("anomalytda_client.anomaly_v2")
logger.setLevel(logging.INFO)
logger.debug("AnomalyV2Model module loaded.")

DEFAULT_BATCH_SIZE: int = 8

# --- Model & Preprocessing Constants ---
MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


class AnomalyV2ModelInferenceResult(TypedDict):
    index: int
    original_pil_resized: Image
    max_score: float
    amap_processed_gray: np.ndarray


class AnomalyV2Model(BaseModel):
    """
    AnomalyV2Model is a class that represents the model for anomaly detection.
    It inherits from the BaseModel class and provides additional functionality
    specific to anomaly detection.

    Attributes:
        model_type (str): The type of the model, which is "anomaly_v2".
        model_name (str): The name of the model, which is "AnomalyV2".
    """

    model_type = "anomaly_v2"
    model_name = "AnomalyV2"

    def __init__(self, anomaly_model_filepath: str, image_size: Tuple[int, int], batch_size: int = DEFAULT_BATCH_SIZE):
        super().__init__(anomaly_model_filepath)
        self.image_size = image_size
        self.batch_size = batch_size

    @property
    def ort_session(self) -> ort.InferenceSession:
        """
        Loads the model session from the anomaly model file path.

        Returns:
            ort.InferenceSession: The loaded model session.
        """
        if not hasattr(self, "_ort_session"):
            self._ort_session: ort.InferenceSession = self._load_model_session("simplified2.onnx")

        return self._ort_session

    def inference(self, images_set: List[Image]) -> List[AnomalyV2ModelInferenceResult]:
        all_data: List[AnomalyV2ModelInferenceResult] = []  # To store results for all images

        num_images = len(images_set)
        batches_bar = trange(0, num_images, self.batch_size, desc="Detecting anomalies", unit="batch")
        for i in batches_bar:
            batch_images = images_set[i : i + self.batch_size]
            actual_batch_size = len(batch_images)
            batches_bar.set_postfix_str(f"images {i+1}-{i + actual_batch_size} of {num_images}")

            batch_input_list = []
            batch_original_pil_resized_list = []
            batch_image_indices = []

            for k, image in enumerate(batch_images):
                try:
                    original_pil_image = image.convert("RGB")
                    resized_pil_image = original_pil_image.resize(self.image_size)

                    image_np = np.array(resized_pil_image).astype(np.float32) / 255.0
                    image_normalized = (image_np - MEAN) / STD
                    image_transposed = image_normalized.transpose((2, 0, 1))  # CHW

                    batch_input_list.append(image_transposed)
                    batch_original_pil_resized_list.append(resized_pil_image)
                    batch_image_indices.append(i + k)
                except Exception as e:
                    logger.error(f"Skipping image {i + k + 1} due to preprocessing error: {e}")
                    # Add placeholders if you need to maintain batch structure strictly for post-processing indices
                    # For now, we'll just have a smaller actual batch if an image fails
                    continue

            if not batch_input_list:
                logger.warning(f"Skipping empty batch {i // self.batch_size + 1}")
                continue

            current_valid_items_in_batch = len(batch_input_list)

            # Pad the batch if it's smaller than MODEL_BATCH_SIZE
            input_tensor_list = list(batch_input_list)  # Make a mutable copy
            if current_valid_items_in_batch < self.batch_size:
                num_padding = self.batch_size - current_valid_items_in_batch
                if current_valid_items_in_batch > 0:  # Check if there's at least one valid image to pad with
                    padding_image_data = batch_input_list[-1]  # Use the last valid image for padding
                    for _ in range(num_padding):
                        input_tensor_list.append(np.copy(padding_image_data))
                    logger.info(f"Padded batch with {num_padding} repetitions of the last image.")
                else:  # Should not happen if we `continue` on empty batch_input_list
                    logger.info("Error: Trying to pad an empty batch.")
                    continue

            input_tensor = np.stack(input_tensor_list, axis=0).astype(np.float32)

            # ONNX Inference
            try:
                input_name = self.ort_session.get_inputs()[0].name
                model_output_list = self.ort_session.run(None, {input_name: input_tensor})
                inference_result_batched = model_output_list[
                    0
                ]  # Shape e.g. (MODEL_BATCH_SIZE, H_model, W_model) or (MODEL_BATCH_SIZE, C_model, H_model, W_model)
            except Exception as e:
                logger.info(f"Error during ONNX inference for batch starting with {i+1}: {e}")
                import traceback

                traceback.print_exc()
                continue  # Skip to next batch

            # Process each item in the batch output (only up to actual_batch_size)
            for k in range(current_valid_items_in_batch):
                image_index_k = batch_image_indices[k]  # Original index of the image in the input list
                original_pil_resized_k = batch_original_pil_resized_list[k]

                # Extract the k-th sample's output from the batch
                # The logic here must replicate what worked for a single image, now applied to inference_result_batched[k]

                if inference_result_batched.ndim == 3:  # Output is (Batch, H_model, W_model), e.g., (8, 36, 36)
                    # For sample k, its map is inference_result_batched[k], shape (H_model, W_model)
                    sample_k_map_hw = inference_result_batched[k]
                    # To match the previous logic: np.expand_dims(batched_output, axis=1)[0] resulted in (1,H,W)
                    # So, for a single (H,W) map, we make it (1,H,W)
                    intermediate_map_chw_k = np.expand_dims(sample_k_map_hw, axis=0)  # (1, H_model, W_model)

                elif (
                    inference_result_batched.ndim == 4
                ):  # Output is (Batch, C_model, H_model, W_model), e.g., (8, 1, 36, 36)
                    # For sample k, its map is inference_result_batched[k], shape (C_model, H_model, W_model)
                    # To match the previous logic: batched_output[0] resulted in (C,H,W)
                    intermediate_map_chw_k = inference_result_batched[k]  # (C_model, H_model, W_model)
                else:
                    logger.info(
                        f"Model output tensor for image {image_index_k} has unexpected ndim: {inference_result_batched.ndim}"
                    )
                    continue

                # Transpose to (H, W, C) for max score and cv2 operations
                amap_raw_hwc_k = intermediate_map_chw_k.transpose((1, 2, 0))  # (H_model, W_model, C_eff)
                current_max_score_k = np.max(amap_raw_hwc_k)

                # Anomaly map processing (resize, blur)
                amap_resized_k = cv2.resize(amap_raw_hwc_k, self.image_size, interpolation=cv2.INTER_LINEAR)
                if amap_resized_k.ndim == 2:
                    amap_resized_k = np.expand_dims(amap_resized_k, axis=-1)

                amap_blurred_k = cv2.GaussianBlur(amap_resized_k, (33, 33), 4)
                if amap_blurred_k.ndim == 2:
                    amap_blurred_k = np.expand_dims(amap_blurred_k, axis=-1)

                all_data.append(
                    AnomalyV2ModelInferenceResult(
                        index=image_index_k,
                        original_pil_resized=original_pil_resized_k,
                        max_score=current_max_score_k,
                        amap_processed_gray=amap_blurred_k,  # (H,W,1) float
                    )
                )

        return all_data
