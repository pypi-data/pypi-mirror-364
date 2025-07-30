import math
import os
from typing import List, Optional, Tuple

import numpy as np
import onnxruntime as ort
from PIL.Image import Image
from scipy.ndimage import gaussian_filter
from tqdm.auto import tqdm, trange

from anomalytda_client.constants import anomaly_crop_cols_default, anomaly_crop_rows_default, batch_size_default
from anomalytda_client.files import get_filenames
from anomalytda_client.internal._model import BaseModel
from anomalytda_client.internal._transforms import get_test_transforms_cpu, get_test_transforms_cpu_from_images
from anomalytda_client.tools import cvt2heatmap, min_max_norm, show_cam_on_image, zoom_anomaly_maps


def get_model_session(models_root: str, model_name: str) -> ort.InferenceSession:
    model_filepath: str = os.path.join(models_root, model_name)
    assert os.path.isfile(model_filepath)
    return ort.InferenceSession(model_filepath)


def combine_images_cpu(images: List[np.ndarray], rows: int, cols: int) -> np.ndarray:
    if images[0].ndim == 2:  # single channel images
        combined_rows = []
        for r in range(rows):
            # Concatenate images horizontally to form a single row
            row_images = images[r * cols : (r + 1) * cols]
            combined_row = np.concatenate(row_images, axis=-1)  # numpy version
            combined_rows.append(combined_row)

        # Now, concatenate all rows vertically
        combined_image = np.concatenate(combined_rows, axis=-2)  # numpy version
    else:  # multi channel images
        combined_rows = []
        for r in range(rows):
            # Concatenate the images in this row along the width (axis=1, which is dim=-2 for tensors)
            row_images = images[r * cols : (r + 1) * cols]
            combined_row = np.concatenate(row_images, axis=1)  # numpy version
            combined_rows.append(combined_row)

        # Now, concatenate the combined rows along the height (axis=0, which is dim=-3 for tensors)
        combined_image = np.concatenate(combined_rows, axis=0)  # numpy version

    return combined_image


def get_combined_anomaly_maps(
    fs_list: np.ndarray, ft_list: np.ndarray, crop_rows: int, crop_cols: int
) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    combined_anomaly_maps: List[np.ndarray] = []
    sim_vector_list: List[np.ndarray] = []
    fs = fs_list[:, :, :, :]
    ft = ft_list[:, :, :, :]

    dot_product = np.sum(fs * ft, axis=1)  # shape: (72, 14, 14)
    fs_norm = np.linalg.norm(fs, axis=1)  # shape: (72, 14, 14)
    ft_norm = np.linalg.norm(ft, axis=1)  # shape: (72, 14, 14)
    cosine_similarity = dot_product / (fs_norm * ft_norm + 1e-8)  # Add small value to avoid division by zero
    a_map = 1 - cosine_similarity

    sim_vector = a_map.copy()

    a_map = np.expand_dims(a_map, axis=1)  # numpy version

    # Combine the anomaly maps
    for i in range(len(ft_list) // (crop_rows * crop_cols)):
        images = [a_map[i * crop_rows * crop_cols + j][0] for j in range(crop_rows * crop_cols)]
        combined_anomaly_maps.append(combine_images_cpu(images, crop_rows, crop_cols))
        sim_vector_list.append(
            sim_vector[i * (crop_rows * crop_cols) : (i + 1) * (crop_rows * crop_cols), :, :]
        )  # Store sim_vector for the corresponding set of 4

    return combined_anomaly_maps, sim_vector_list


def cal_anomaly_map_cpu(
    fs_list, ft_list, image_size, crop_rows, crop_cols, out_size=224, amap_mode="mul"
) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    # Combine the anomaly maps
    combined_anomaly_maps, sim_vector_list = get_combined_anomaly_maps(
        fs_list=fs_list, ft_list=ft_list, crop_rows=crop_rows, crop_cols=crop_cols
    )

    a_map_list: List[np.ndarray] = zoom_anomaly_maps(
        combined_anomaly_maps=combined_anomaly_maps, new_size=(image_size[0] * crop_rows, image_size[1] * crop_cols)
    )

    return a_map_list, sim_vector_list


def get_anomalies(
    models_root: str,
    test_root: str,
    crop_rows: Optional[int] = None,
    crop_cols: Optional[int] = None,
    batch_size: Optional[int] = None,
) -> Tuple[List[Tuple[np.uint8, np.ndarray]], List[float], List[str]]:
    crop_rows = crop_rows or anomaly_crop_rows_default
    crop_cols = crop_cols or anomaly_crop_cols_default
    batch_size = batch_size or batch_size_default
    img_list: List[Tuple[np.uint8, np.ndarray]] = []
    score_list: List[float] = []

    encoder_session: ort.InferenceSession = get_model_session(models_root=models_root, model_name="encoder.onnx")
    bn_session: ort.InferenceSession = get_model_session(models_root=models_root, model_name="bn.onnx")
    decoder_session: ort.InferenceSession = get_model_session(models_root=models_root, model_name="decoder.onnx")

    image_size = tuple(encoder_session._inputs_meta[0].shape[-2:])

    filenames: List[str] = get_filenames(image_folder=test_root)

    for img in tqdm(
        get_test_transforms_cpu(test_root, image_size, crop_rows, crop_cols, batch_size),
        desc="Detecting anomalies",
        total=math.ceil(len(filenames) / batch_size),
        unit="batch",
    ):
        # Reshape the input: [batch_size, 4, 3, 224, 224] -> [batch_size * 4, 3, 224, 224]
        batch_size, num_quadrants, channels, height, width = img.shape
        img = img.reshape(batch_size * num_quadrants, channels, height, width)
        numpy_img = img.astype(np.float32)
        inputs = encoder_session.run(None, {"input": numpy_img})
        bn_outputs = bn_session.run(None, {"input": inputs[0], "input.13": inputs[1], "onnx::Concat_2": inputs[2]})
        outputs = decoder_session.run(None, {"input": bn_outputs[0]})

        amap_list, _ = cal_anomaly_map_cpu(
            inputs[-1],
            outputs[-1],
            out_size=img.shape[-1],
            image_size=image_size,
            crop_rows=crop_rows,
            crop_cols=crop_cols,
            amap_mode="acc",
        )

        # Prepare the images for visualization by permuting the axes
        imgs_vis = img.transpose(0, 2, 3, 1)  # numpy

        imgs_vis_combined = []
        for i in trange(len(imgs_vis) // num_quadrants, desc="Combine images", unit="image"):
            # Extract the corresponding quadrant images for this batch
            images = [imgs_vis[i * num_quadrants + j] for j in range(num_quadrants)]

            # Combine the images into a larger grid (e.g., 2x2, 3x3, etc.)
            combined_map = combine_images_cpu(images, crop_rows, crop_cols)

            # Append the combined image to the list for further processing or visualization
            imgs_vis_combined.append(combined_map)

        for i, amap in tqdm(
            enumerate(amap_list), desc="Render anomalies on images", total=len(amap_list), unit="image"
        ):
            score_list.append(amap.max())
            anomaly_map = gaussian_filter(amap, sigma=4)
            ano_map = min_max_norm(anomaly_map)
            ano_map = (ano_map * -1) + 1
            ano_map = cvt2heatmap(ano_map * 255)
            img_vis_c = imgs_vis_combined[i]  # cpu version
            img_vis = np.uint8(min_max_norm(img_vis_c) * 255)  # numpu
            # img_vis = cv2.cvtColor(img_vis_c, cv2.COLOR_BGR2RGB)
            ano_map = show_cam_on_image(img_vis, ano_map)  # type: ignore
            img_list.append((img_vis, ano_map))

    return img_list, score_list, filenames


class AnomalyModel(BaseModel):
    def __init__(
        self,
        anomaly_model_filepath: str,
        crop_rows: Optional[int] = None,
        crop_cols: Optional[int] = None,
        batch_size: Optional[int] = None,
    ) -> None:
        """
        Initial model for anomaly inference from pretrained model on DataRefiner

        :param anomaly_model_filepath: Path to pretrained anomaly model
        :param crop_rows: Number of rows for crop images
        :param crop_cols: Number of cols for crop images
        :param batch_size: Batch size for inference process
        """
        self.anomaly_model_filepath: str = anomaly_model_filepath
        self.crop_rows: int = crop_rows or anomaly_crop_rows_default
        self.crop_cols: int = crop_cols or anomaly_crop_cols_default
        self.batch_size: int = batch_size or batch_size_default

        assert os.path.isfile(self.anomaly_model_filepath), "Not found anomaly model"
        assert self.crop_rows == self.crop_cols, "Must be equal crop row and cols"

    @property
    def encoder_session(self) -> ort.InferenceSession:
        if not hasattr(self, "_encoder_session"):
            self._encoder_session: ort.InferenceSession = self._load_model_session("encoder.onnx")
        return self._encoder_session

    @property
    def bn_session(self) -> ort.InferenceSession:
        if not hasattr(self, "_bn_session"):
            self._bn_session: ort.InferenceSession = self._load_model_session("bn.onnx")
        return self._bn_session

    @property
    def decoder_session(self) -> ort.InferenceSession:
        if not hasattr(self, "_decoder_session"):
            self._decoder_session: ort.InferenceSession = self._load_model_session("decoder.onnx")
        return self._decoder_session

    def inference(self, images_set: List[Image]) -> List[np.ndarray]:
        image_size: Tuple[int, int] = tuple(self.encoder_session._inputs_meta[0].shape[-2:])

        combined_anomaly_maps: List[np.ndarray] = []
        for img in tqdm(
            get_test_transforms_cpu_from_images(
                images_set, image_size, self.crop_rows, self.crop_cols, self.batch_size
            ),
            desc="Detecting anomalies",
            total=math.ceil(len(images_set) / self.batch_size),
            unit="batch",
        ):
            # Reshape the input: [batch_size, 4, 3, 224, 224] -> [batch_size * 4, 3, 224, 224]
            batch_size, num_quadrants, channels, height, width = img.shape
            img = img.reshape(batch_size * num_quadrants, channels, height, width)
            numpy_img = img.astype(np.float32)
            inputs = self.encoder_session.run(None, {"input": numpy_img})
            bn_outputs = self.bn_session.run(
                None, {"input": inputs[0], "input.13": inputs[1], "onnx::Concat_2": inputs[2]}
            )
            outputs = self.decoder_session.run(None, {"input": bn_outputs[0]})

            _combined_anomaly_maps, _ = get_combined_anomaly_maps(
                inputs[-1], outputs[-1], crop_rows=self.crop_rows, crop_cols=self.crop_cols
            )
            combined_anomaly_maps.extend(_combined_anomaly_maps)
        return combined_anomaly_maps
