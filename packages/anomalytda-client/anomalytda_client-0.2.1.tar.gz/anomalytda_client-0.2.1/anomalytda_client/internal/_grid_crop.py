class GridCrop:
    def __init__(self, rows=2, cols=2):
        """
        Args:
            rows (int): Number of rows to split the image into.
            cols (int): Number of columns to split the image into.
        """
        self.rows = rows
        self.cols = cols

    def __call__(self, img):
        width, height = img.size
        crop_width, crop_height = width // self.cols, height // self.rows

        crops = []

        # Split the image into a grid based on rows and columns
        for row in range(self.rows):
            for col in range(self.cols):
                left = col * crop_width
                upper = row * crop_height
                right = (col + 1) * crop_width
                lower = (row + 1) * crop_height

                crops.append(img.crop((left, upper, right, lower)))

        return crops
