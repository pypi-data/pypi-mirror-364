from typing import Generator, List, Tuple

import numpy as np
from PIL import Image

from anomalytda_client.constants import anomaly_imagenet_mean, anomaly_imagenet_std
from anomalytda_client.files import get_filenames
from anomalytda_client.internal._grid_crop import GridCrop


def get_test_transforms_cpu(
    image_folder: str,
    image_size: Tuple[int, int] = (224, 224),
    crop_rows: int = 2,
    crop_cols: int = 2,
    batch_size: int = 32,
) -> Generator[np.ndarray, None, None]:
    """
    Generator to process images in batches, applying grid cropping, resizing, and normalization for ONNX inference.

    Args:
        image_folder (str): Path to the folder containing images.
        image_size (tuple): Target image size for resizing.
        crop_rows (int): Number of rows for grid cropping.
        crop_cols (int): Number of columns for grid cropping.
        batch_size (int): Number of images in each batch.

    Yields:
        numpy.ndarray: Batch of processed images, shape (batch_size, num_crops, 224, 224, 3).
    """

    batch = []
    for idx, image_path in enumerate(get_filenames(image_folder=image_folder)):
        # Load image
        image = Image.open(image_path)

        # Stack crops into a single array for this image and add to batch
        batch.append(
            _transform_image(image=image, image_size=image_size, crop_rows=crop_rows, crop_cols=crop_cols)
        )  # shape: (num_crops, 224, 224, 3)

        # Yield batch when it reaches the batch size
        if (idx + 1) % batch_size == 0:
            yield np.transpose(np.stack(batch, axis=0), (0, 1, 4, 2, 3))  # shape: (batch_size, num_crops, 3, 224, 224)
            batch = []

    # Yield any remaining images in the last batch
    if batch:
        yield np.transpose(np.stack(batch, axis=0), (0, 1, 4, 2, 3))


def get_test_transforms_cpu_from_images(
    images_set: List[Image.Image],
    image_size: Tuple[int, int] = (224, 224),
    crop_rows: int = 2,
    crop_cols: int = 2,
    batch_size: int = 32,
) -> Generator[np.ndarray, None, None]:
    for offset in range(0, len(images_set), batch_size):
        yield np.transpose(
            np.stack(
                [
                    _transform_image(image=image, image_size=image_size, crop_rows=crop_rows, crop_cols=crop_cols)
                    for image in images_set[offset : offset + batch_size]
                ],
                axis=0,
            ),
            (0, 1, 4, 2, 3),
        )  # shape: (batch_size, num_crops, 3, 224, 224)


def _transform_image(
    image: Image.Image, image_size: Tuple[int, int] = (224, 224), crop_rows: int = 2, crop_cols: int = 2
) -> np.ndarray:
    grid_crop = GridCrop(rows=crop_rows, cols=crop_cols)

    if image.mode != "RGB":
        image = image.convert(mode="RGB")

    # Apply GridCrop to the image
    crops = grid_crop(image)

    # Resize and normalize each crop
    processed_crops = []
    for crop in crops:
        resized_crop = crop.resize(image_size, Image.Resampling.LANCZOS)
        np_crop = np.array(resized_crop).astype(np.float32) / 255.0
        normalized_crop = (np_crop - anomaly_imagenet_mean) / anomaly_imagenet_std
        processed_crops.append(normalized_crop)

    # Stack crops into a single array for this image and add to batch
    return np.stack(processed_crops, axis=0)  # shape: (num_crops, 224, 224, 3)
