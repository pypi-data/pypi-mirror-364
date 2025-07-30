from abc import ABC, abstractmethod
from typing import Any, List
from zipfile import ZipFile

import onnxruntime as ort
from PIL.Image import Image


class BaseModel(ABC):
    def __init__(self, anomaly_model_filepath: str) -> None:
        self.anomaly_model_filepath: str = anomaly_model_filepath

    def _load_model_session(self, model_name: str) -> ort.InferenceSession:
        with ZipFile(self.anomaly_model_filepath) as zip_fn:
            with zip_fn.open(model_name) as fn:
                return ort.InferenceSession(fn.read())

    @abstractmethod
    def inference(self, images_set: List[Image], *args, **kwargs) -> List[Any]:
        pass
