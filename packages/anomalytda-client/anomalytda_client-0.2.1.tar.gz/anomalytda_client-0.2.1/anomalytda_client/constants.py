import os
from typing import Tuple

base_dir: str = os.path.dirname(os.path.abspath(__file__))
project_dir: str = os.path.join(base_dir, "..")

batch_size_default: int = 16

anomaly_crop_rows_default: int = 1
anomaly_crop_cols_default: int = 1
anomaly_imagenet_mean: Tuple[float, float, float] = (0.485, 0.456, 0.406)
anomaly_imagenet_std: Tuple[float, float, float] = (0.229, 0.224, 0.225)
