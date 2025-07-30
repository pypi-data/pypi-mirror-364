from typing import List, Tuple

import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import find_objects, gaussian_filter, label, zoom
from tqdm.auto import tqdm


def min_max_norm(image: np.ndarray) -> np.ndarray:
    a_min, a_max = image.min(), image.max()
    return (image - a_min) / (a_max - a_min)


def cvt2heatmap(gray: np.ndarray) -> np.ndarray:
    heatmap = cv2.applyColorMap(np.uint8(gray), cv2.COLORMAP_JET)  # type: ignore
    return heatmap


def show_cam_on_image(img: np.uint8, anomaly_map: np.ndarray) -> np.uint8:
    cam = np.float32(anomaly_map) / 255 + np.float32(img) / 255
    cam = cam / np.max(cam)
    return np.uint8(255 * cam)


def zoom_anomaly_maps(combined_anomaly_maps: List[np.ndarray], new_size: Tuple[int, int]) -> List[np.ndarray]:
    a_map_list = []

    for combined_map in combined_anomaly_maps:
        expanded_combined_map = np.expand_dims(np.expand_dims(combined_map, axis=0), axis=0)
        zoom_factors = (
            new_size[0] / expanded_combined_map.shape[2],  # height zoom
            new_size[1] / expanded_combined_map.shape[3],  # width zoom
        )
        combined_map = zoom(
            expanded_combined_map, (1, 1, zoom_factors[1], zoom_factors[0]), order=1
        )  # order=1 for bilinear

        # Store results
        a_m = combined_map[0, 0, :, :]
        a_map_list.append(a_m)
    return a_map_list


def get_images_amaps_score(
    images_set: List[Image.Image], amap_list: List[np.ndarray]
) -> Tuple[List[Tuple[np.ndarray, np.ndarray]], List[float]]:
    img_list: List[Tuple[np.ndarray, np.ndarray]] = []
    score_list: List[float] = []

    for i, amap in tqdm(
        enumerate(zoom_anomaly_maps(amap_list, images_set[0].size)),
        desc="Render anomalies on images",
        total=len(amap_list),
        unit="image",
    ):
        score_list.append(amap.max())
        anomaly_map = gaussian_filter(amap, sigma=4)
        ano_map = min_max_norm(anomaly_map)
        ano_map = (ano_map * -1) + 1
        ano_map = cvt2heatmap(ano_map * 255)
        img_vis = np.array(images_set[i].resize(ano_map.shape[:-1][::-1], Image.Resampling.LANCZOS))
        ano_map = show_cam_on_image(img_vis, ano_map)  # type: ignore
        img_list.append((img_vis, ano_map))

    return img_list, score_list


def find_bounding_boxes(amap: np.ndarray, image_size: Tuple[int, int], threshold: float = 0.5):
    if amap.ndim == 3 and amap.shape[-1] == 1:
        amap = amap.squeeze(axis=-1)
    elif amap.ndim == 2:
        amap = amap
    else:
        raise ValueError(f"amap must be grayscale (H, W) or (H, W, 1), got shape {amap.shape}")

    sx, sy = np.shape(amap)
    zoom_factors: Tuple[float, float] = (image_size[0] / sx, image_size[1] / sy)
    amap_zoomed: np.ndarray = zoom(amap, zoom_factors, order=1)  # order=1 for bilinear

    binary_map = amap_zoomed > threshold

    # Label connected components
    labeled_array, _ = label(binary_map)

    # Find bounding boxes around hot spots
    hotspot_slices = find_objects(labeled_array)

    boxes: List[Tuple[int, int, int, int]] = [
        (
            hotspot_slice[1].start,  # x_min
            hotspot_slice[0].start,  # y_min
            hotspot_slice[1].stop,  # x_max,
            hotspot_slice[0].stop,  # y_max
        )
        for hotspot_slice in hotspot_slices
        if hotspot_slice is not None
    ]

    return boxes
