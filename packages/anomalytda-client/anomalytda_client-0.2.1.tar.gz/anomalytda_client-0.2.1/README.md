**Readme**

The AnomalyTDA Client Library is a Python API toolkit that facilitates seamless integration between your Python code and the DataRefiner AnomalyTDA platform, allowing users to perform inference on their data using models exported from the AnomalyTDA platform.

**Website**: [https://datarefiner.com](https://datarefiner.com)

### What functions this library support? ###

* Perform anomaly detection using exported models 
* Perform detection using supervised models exported from AnomalyTDA platform
* Generate anomaly heatmaps and bounding boxes images

### Usage example for Anomaly Detection use case: 
###

```
import os
from typing import List, Tuple

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from scipy.ndimage import zoom

from tqdm.notebook import tqdm

from anomalytda_client import AnomalyModel
from anomalytda_client.files import get_filenames
from anomalytda_client.tools import get_images_amaps_score, find_bounding_boxes

anomaly_model_filepath: str = "models/exported_model.anomaly"
image_folder: str = "data/myimages"

# Get filenames
filenames = get_filenames(image_folder)

# Reading all images and converting grayscale images to RGB while keeping filenames
test_images_set: List[Tuple[str, Image.Image]] = [
    Image.open(filename).convert("RGB") for filename in tqdm(filenames, desc="Read images")
]

# Applying anomaly detection model to the images, and getting anomaly map in return
anomaly_model: AnomalyModel = AnomalyModel(
    anomaly_model_filepath=anomaly_model_filepath, 
    crop_rows=2, # Grid crop "rows" parameter used during the model training
    crop_cols=2, # Grid crop "columns" parameter used during the model training
    batch_size=8
)
amap_list: List[np.ndarray] = anomaly_model.inference(test_images_set)

# Using anomaly maps for each image to generate the image heatmaps and to get anomaly scores
img_list, score_list = get_images_amaps_score(images_set=test_images_set, amap_list=amap_list)

# Calculate anomaly threshold for bounding boxes
threshold = np.percentile(np.array(amap_list), 99)

# Visualise images and generate bounding boxes around the anomalies
import matplotlib.patches as patches

for i in np.array(score_list).argsort()[::-1][:200]:
    print('score:', score_list[i], 'filename:', filenames[i])
    img, ano_map = img_list[i]
    data = amap_list[i]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6, 3))
    ax1.imshow(img)
    ax1.axis('off')
    ax2.imshow(ano_map)
    ax2.axis('off')

    for x_min, y_min, x_max, y_max in find_bounding_boxes(
        amap=data, image_size=np.shape(img), threshold=threshold
    ):
        ax2.add_patch(patches.Rectangle(
            xy=(x_min, y_min), width=x_max - x_min, height=y_max - y_min,
            linewidth=2, edgecolor="red", facecolor="none",
        ))
    
    plt.tight_layout()
    plt.show()
```

### Usage example for Detection use case: 
###

```
import os
import math
from typing import List

import cv2
import numpy as np
import onnxruntime as ort
import matplotlib.pyplot as plt
from PIL import Image
from tqdm.auto import trange

from anomalytda_client import DetectionModel
from anomalytda_client.files import get_filenames

detection_model_filepath: str = "models/exported_model.detection"
image_folder: str = "data/myimages"

# Reading all images from the folder in RAM
test_images_set: List[Image.Image] = [Image.open(filename) for filename in get_filenames(image_folder)]
len(test_images_set)

# Initialise detection model
detection_model: DetectionModel = DetectionModel(
    anomaly_model_filepath=detection_model_filepath, batch_size=16
)

# Run detection model to predict the bounding boxes
outputs: List[np.ndarray] = detection_model.inference(
    images_set=test_images_set, 
    conf=0.1, 
    iou=0.45,
    image_size=(640, 640)
)

# Show the results
for i, result in enumerate(outputs):
    image: np.ndarray = np.array(test_images_set[i].convert("RGB"))
    image = image[:, :, ::-1].copy()
    print(f"Filename: {os.path.basename(test_images_set[i].filename)}")
    for box, score, class_ in result:
        print(f"Score: {score:.2f}, class: {class_} = {result.names[class_]}")
        x1, y1, x2, y2 = box[0], box[1], box[0] + box[2], box[1] + box[3]
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(image, f"{result.names[class_]}: {score:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Display the images
    _, (ax1, ax2) = plt.subplots(1, 2, figsize=(6, 3))
    ax1.imshow(test_images_set[i])
    ax1.axis('off')
    ax2.imshow(cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    ax2.axis('off')
    plt.tight_layout()
    plt.show()
```