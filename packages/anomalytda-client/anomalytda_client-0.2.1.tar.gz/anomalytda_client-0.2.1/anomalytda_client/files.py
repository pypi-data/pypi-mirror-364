import os
from typing import AnyStr, List


def get_filenames(image_folder) -> List[AnyStr]:
    """
    Collect all image paths from the folder and its subfolders

    Args:
        image_folder ([AnyStr]): Folder containing all images
    Return:
        [AnyStr]: List of all image paths
    """
    image_paths: List[AnyStr] = [
        os.path.join(root, img)
        for root, _, files in os.walk(image_folder)
        for img in files
        if img.endswith((".jpg", ".png"))
    ]
    return image_paths
