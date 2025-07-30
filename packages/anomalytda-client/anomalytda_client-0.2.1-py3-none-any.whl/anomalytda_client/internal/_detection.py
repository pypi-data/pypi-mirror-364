import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import onnxruntime as ort
from PIL.Image import Image
from tqdm.auto import tqdm, trange

from anomalytda_client.constants import batch_size_default
from anomalytda_client.internal._model import BaseModel

logger: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DetectionResult:
    boxes: List[Tuple[int, int, int, int]]
    scores: List[float]
    class_indices: List[int]
    _model: "DetectionModel"

    def __iter__(self):
        return zip(self.boxes, self.scores, self.class_indices)

    @property
    def names(self) -> Dict[int, str]:
        return self._model.names


def _preprocess(batch_images: List[Image], input_size: Optional[int] = None) -> Tuple[List[np.ndarray], List[float]]:
    """
    Preprocess images for the model:
    - Convert image from PIL format to NumPy format.
    - Convert image from RGBA to RGB if needed.
    - Resize image to 640x640 pixels.
    - Normalize pixel values.
    - Change channel order to "channel-first".

    :param batch_images: List of images in PIL format.
    :param input_size: Image size in pixels.
    :return: List of preprocessed images in NumPy format.
    """
    input_size = input_size or 640
    preprocessed_images: List[np.ndarray] = []
    scales: List[float] = []
    for image in tqdm(batch_images, desc="Preprocessing images batch"):
        image_np = np.array(image if image.mode == "RGB" else image.convert("RGB"))

        shape = image_np.shape
        ratio = float(shape[0]) / shape[1]
        if ratio > 1:
            h = input_size
            w = int(h / ratio)
        else:
            w = input_size
            h = int(w * ratio)
        scale = float(h) / shape[0]
        scales.append(scale)

        image_np = cv2.resize(image_np, (w, h))

        det_image: np.ndarray = np.zeros((input_size, input_size, 3), dtype=np.uint8)
        det_image[:h, :w, :] = image_np

        det_image = det_image.astype(np.float32) / 255.0
        det_image = np.transpose(det_image, (2, 0, 1))
        preprocessed_images.append(det_image)
    preprocessed_images = np.stack(preprocessed_images, axis=0)
    return preprocessed_images, scales


def _postprocessing(
    outputs: np.ndarray, scale: float = 1.0, confidence_threshold: float = 0.1
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Post-process model outputs:
    - Extract class scores and bounding box coordinates.
    - Filter detections based on a confidence threshold.
    - Scale bounding box coordinates.

    :param outputs: Model outputs.
    :param scale: Scale for bounding box coordinates.
    :param confidence_threshold: Confidence threshold for filtering detections.
    :return: Scaled bounding box coordinates, filtered scores, and class indices.
    """
    class_scores = outputs[:, 4:]
    bounding_boxes = outputs[:, :4]

    max_scores = np.max(class_scores, axis=1)
    class_ids = np.argmax(class_scores, axis=1)

    valid_indices = np.where(max_scores >= confidence_threshold)[0]

    valid_boxes = bounding_boxes[valid_indices]
    valid_scores = max_scores[valid_indices]
    valid_class_ids = class_ids[valid_indices]

    left = np.maximum(0, ((valid_boxes[:, 0] - valid_boxes[:, 2] / 2) / scale).astype(int))
    top = np.maximum(0, ((valid_boxes[:, 1] - valid_boxes[:, 3] / 2) / scale).astype(int))
    width = (valid_boxes[:, 2] / scale).astype(int)
    height = (valid_boxes[:, 3] / scale).astype(int)

    scaled_boxes = np.stack([left, top, width, height], axis=1)

    return scaled_boxes, valid_scores, valid_class_ids


def _non_max_suppression_per_class(
    boxes: np.ndarray, scores: np.ndarray, class_indices: np.ndarray, conf_thres: float = 0.25, iou_thres: float = 0.45
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Perform Non-Maximum Suppression (NMS) per class:
    - Filter out bounding boxes with low confidence.
    - Apply NMS for each unique class.

    :param boxes: Bounding boxes.
    :param scores: Confidence scores.
    :param class_indices: Class indices.
    :param conf_thres: Confidence threshold for filtering.
    :param iou_thres: IoU threshold for NMS.
    :return: DetectionResult object with filtered boxes, scores, and class indices.
    """
    keep = scores >= conf_thres
    boxes, scores, class_indices = boxes[keep], scores[keep], class_indices[keep]

    if len(boxes) == 0:
        return np.array([]), np.array([]), np.array([])

    unique_classes = np.unique(class_indices)
    final_boxes = []
    final_scores = []
    final_class_indices = []

    for cls_ in unique_classes:
        cls_mask = class_indices == cls_
        cls_boxes = boxes[cls_mask]
        cls_scores = scores[cls_mask]
        cls_class_indices = class_indices[cls_mask]

        indices = np.argsort(cls_scores)[::-1]
        cls_boxes, cls_scores, cls_class_indices = cls_boxes[indices], cls_scores[indices], cls_class_indices[indices]

        while len(cls_boxes) > 0:
            current_box = cls_boxes[0]
            final_boxes.append(current_box)
            final_scores.append(cls_scores[0])
            final_class_indices.append(cls_class_indices[0])

            x1 = np.maximum(current_box[0], cls_boxes[1:, 0])
            y1 = np.maximum(current_box[1], cls_boxes[1:, 1])
            x2 = np.minimum(current_box[0] + current_box[2], cls_boxes[1:, 0] + cls_boxes[1:, 2])
            y2 = np.minimum(current_box[1] + current_box[3], cls_boxes[1:, 1] + cls_boxes[1:, 3])

            inter_area = np.maximum(0, x2 - x1) * np.maximum(0, y2 - y1)
            box_area = current_box[2] * current_box[3]
            other_areas = cls_boxes[1:, 2] * cls_boxes[1:, 3]

            iou = inter_area / (box_area + other_areas - inter_area)

            mask = iou <= iou_thres
            cls_boxes = cls_boxes[1:][mask]
            cls_scores = cls_scores[1:][mask]
            cls_class_indices = cls_class_indices[1:][mask]

    return np.array(final_boxes), np.array(final_scores), np.array(final_class_indices)


class DetectionModel(BaseModel):
    def __init__(
        self,
        anomaly_model_filepath: str,
        image_size: Optional[Tuple[int, int]] = None,
        batch_size: Optional[int] = None,
    ) -> None:
        """
        Constructor for the anomaly detection model.

        :param anomaly_model_filepath: Path to the anomaly model file.
        :param image_size: Model image size.
        :param batch_size: Batch size for processing images.
        """
        self.anomaly_model_filepath: str = anomaly_model_filepath
        self.image_size: Tuple[int, int] = image_size or (640, 640)
        self.batch_size: int = max(2, batch_size or batch_size_default)

    @property
    def session(self) -> ort.InferenceSession:
        """
        Creates and returns a session for performing inference using the ONNX model.

        :return: ONNX inference session.
        """
        if not hasattr(self, "_session"):
            self._session: ort.InferenceSession = self._load_model_session(model_name="best.onnx")

            # TODO: Delete debug information after test detection
            logger.debug("Model inputs:")
            for input in self._session.get_inputs():
                logger.debug(f"Name: {input.name}, Shape: {input.shape}, Type: {input.type}")

            logger.debug("Model outputs:")
            for input in self._session.get_outputs():
                logger.debug(f"Name: {input.name}, Shape: {input.shape}, Type: {input.type}")

        return self._session

    @property
    def names(self) -> Dict[int, str]:
        if not hasattr(self, "_names"):
            self._names: Dict[int, str] = eval(
                self.session.get_modelmeta().custom_metadata_map.get("names", "{0: ''}")
            )
        return self._names

    def inference(
        self, images_set: List[Image], conf: float = 0.1, iou: float = 0.45, *args, **kwargs
    ) -> List[DetectionResult]:
        """
        Performs inference on a set of images.

        :param images_set: List of images in PIL format.
        :param conf: Confidence threshold for filtering detections.
        :param iou: IoU threshold for non-maximum suppression.
        :return: List of inference results in NumPy format.
        """
        results: List[DetectionResult] = []
        for offset in trange(0, len(images_set), self.batch_size, desc="Predicting images batch"):
            input_images, scales = _preprocess(
                batch_images=images_set[offset : offset + self.batch_size], input_size=self.image_size[0]
            )
            outputs = self.session.run(None, {"images": input_images})[0]
            for i in trange(outputs.shape[0], desc="Postprocessing images batch"):
                boxes, scores, class_indices = _postprocessing(
                    outputs=np.transpose(np.squeeze(outputs[i])), scale=scales[i], confidence_threshold=conf
                )
                final_boxes, final_scores, final_class_indices = _non_max_suppression_per_class(
                    boxes=boxes, scores=scores, class_indices=class_indices, conf_thres=conf, iou_thres=iou
                )
                results.append(
                    DetectionResult(
                        boxes=final_boxes.tolist(),
                        scores=final_scores.tolist(),
                        class_indices=list(map(int, final_class_indices)),
                        _model=self,
                    )
                )
        return results
